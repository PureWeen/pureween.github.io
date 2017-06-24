--- 
title:  "Fun with Firebase, Too Many References, ProGuard, and MultiDex"
date:   2017-06-17 00:00:00 -0600
categories: Firebase ProGuard
comments: true
---



The [sample project][PureWeen-Repo] for this post contains the finished project with ProGuard and Firebase setup. This blog is more about dealing with the issue of too many references that comes up when adding Firebase. For specifics on setting up Firebase just check out my [sample project][PureWeen-Repo] and the [Firebase docs][firebase-docs] for how to setup and generate your **google-services.json** file.


After installing the latest Xamarin Support libraries you will most likely receive the following error.

```
error MSB6006: "java.exe" exited with code 2. // :-(
```

If we crank up the build verbosity on Visual Studio.

**Tools -> Options -> Project and Solutions -> Build and Run -> Set build output verbosity to Detailed**


Now we get a much more helpful message

```
2>  trouble writing output: Too many field references to fit in one dex file: 68555; max is 65536. (TaskId:349)
2>  You may try using multi-dex. If multi-dex is enabled then the list of classes for the main dex list is too large. (TaskId:349)
2>  References by package: (TaskId:349)
......
2>    2379 android.support.compat
2>    2379 android.support.coreui
2>    2379 android.support.coreutils
2>    2379 android.support.design
```


Unfortunately you can hit this limit fairly fast with the latest and greatest Xamarin Support libraries. The [sample project][PureWeen-Repo] for this post has the following packages installed.

* HockeyApp
* Xamarin.Firebase
* Xamarin.Forms
* Xamarin.Forms.Maps
* Azure Messaging
* And very little custom code. Just enough to get Firebase working.

I call this a gross overuse of 3rd party libraries. 

## Solution 1: MultiDex 
This solution isn't too hard to get working but it's not the [recommended first solution] [multidex-avoid] and it has some [limitations][multidex-limitations].


The main trickery to overcome with MutiDex comes from an upstream bug when compiling on **Windows**. If not accounted for this will causes your app to most likely crash on Pre-Lollipop. The in depth details of the fix can be found [here][multidex-douglas]


### Quick and dirty summary

* Locate your current build tools directory **android-sdk\build-tools\someversion**

* In there you will see a file called **mainClassesDex.bat**

* And change this section
```
if DEFINED output goto redirect
call "%java_exe%" -Djava.ext.dirs="%frameworkdir%" com.android.multidex.MainDexListBuilder "%disableKeepAnnotated%" "%tmpJar%" "%params%"
goto afterClassReferenceListBuilder
:redirect
call "%java_exe%" -Djava.ext.dirs="%frameworkdir%" com.android.multidex.MainDexListBuilder "%disableKeepAnnotated%" "%tmpJar%" "%params%" 1>"%output%"
:afterClassReferenceListBuilder
```
To
```
SET params=%params:'=%  
if DEFINED output goto redirect  
call "%java_exe%" -Djava.ext.dirs="%frameworkdir%" com.android.multidex.MainDexListBuilder %disableKeepAnnotated% "%tmpJar%" %params%  
goto afterClassReferenceListBuilder  
:redirect
call "%java_exe%" -Djava.ext.dirs="%frameworkdir%" com.android.multidex.MainDexListBuilder %disableKeepAnnotated% "%tmpJar%" %params% 1>"%output%"  
:afterClassReferenceListBuilder
```

Once you've done that you should see a non-empty **multidex.keep** file show up in your **obj/Release** folder and your application should run without any issues on KitKat.


## Solution 2: ProGuard
There's a good chance that once this [bug][xamarin-bug-references] is resolved this won't be as relevant. But for now these are the steps I had to take in order to get **ProGuard** to work
 
In order for **ProGuard** to work the linker has to be [enabled][xamarin-proguard]. I've found that even in **Debug** I have to set the **Linker** to Full (Sdk and User assemblies) in order for my projects to compile.


At this point the dream would be to just enable **ProGuard** and magically it will all work.

But alas we are met with

```
error MSB6006: "java.exe" exited with code 1.
```

That's one exit code closer to zero so we must be on the right track :-p

Because our build logging is still set to **Detailed** (unless you started here in which case go set your build output to Detailed) we can check the output and  see a bunch of **ProGuard** warnings .. Here's a snippet

```
warning : com.google.firebase.messaging.zzc: can't find referenced class com.google.android.gms.measurement.AppMeasurement
...

java.io.IOException: Please correct the above warnings first.
2>  	at proguard.Initializer.execute(Unknown Source)
2>  	at proguard.ProGuard.initialize(Unknown Source)
2>  	at proguard.ProGuard.execute(Unknown Source)
2>  	at proguard.ProGuard.main(Unknown Source)
```


Much like a linker file we're going to need to setup a ProGuard configuration file to help ProGuard out.  

Add a **proguard.cfg** file into your project and set the build action to **ProGuardconfiguration**. Go [here][xamarin-proguard-setup] for more information if needed.

For my project all I needed in order to get rid of the above exception were these two lines.

```
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.android.gms.**
```

Now we have a **ProGuard** file and we're good to go. 

Click compile

```
error MSB6006: "java.exe" exited with code 1. //:-(

1>  proguard.ParseException: Unknown option '∩╗┐-keep' in line 1 of file 'proguard.cfg',
1>    included from argument number 10
1>  	at proguard.ConfigurationParser.parse(Unknown Source)
1>  	at proguard.ProGuard.main(Unknown Source)
```

Googling the exception reveals a bunch of resources talking about how to fix.  Basically you need to encode the file in **UTF-8  Without BOM**.  Fire up [Notepad++][notepad++], open your ProGuard file, and set the Encoding.

```
Encoding > Encode in UTF-8
```

Now re-save the file and try to compile again. At this point you should hopefully be jubilantly thinking or yelling **It compiles!!!!!!!!!!!!!!!!!!!!**

If your project doesn't compile then you'll need to just massage the **proguard.cfg** file as needed based on your build output. 

Once you're able to get the project to compile let's run the application to see what happens.

### There's a good chance that your app will crash at this point 
This means that **ProGuard** has removed something it couldn't figure out you needed. If we check our device logs via [Visual Studio][VS-DeviceLog] or Android Studio we can see the exception that caused the crash. 

It will look something like

```
Caused by: java.lang.ClassNotFoundException: Didn't find class "android.support.v7.widget.FitWindowsFrameLayout"
```


Perfecting this will depend on your specific project.  In order for my app to not crash and throw exceptions like *blankity blank class not found* I had to add the following lines.

```
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.android.gms.**
-keep class com.microsoft.windowsazure.messaging.** { *; }
-dontwarn com.microsoft.windowsazure.messaging.**
-keep class com.google.firebase.** { *; }
-dontwarn com.google.firebase.**
-keep class android.support.v7.widget.** { *; }
-dontwarn android.support.v7.widget.**
-keep class android.support.v4.widget.Space { *; }
-dontwarn android.support.v4.widget.Space
```


My recommendation after getting ProGuard setup would be to click around everywhere in your app and watch the device logs for any class not found exceptions that you'll need to resolve. 


At this point you can hopefully run your app and see this message in your device logs

```
FirebaseApp initialization successful
```


## Notes on Debugging Firebase
Firebase specific log messages are really hard to sift through when you name your project Firebase :-/

### Be aware of the Linker and that it runs before ProGuard
For the [referenced project][PureWeen-Repo] I was able to get Firebase working without having to worry about the Linker but when I initially did this for my own personal project I had to setup a [Linker.xml][xamarin-linker] file for the FirebaseInitProvider. 


``` 
<assembly fullname="Xamarin.Firebase.Common">
    <type fullname="Firebase.Provider.FirebaseInitProvider" />
 </assembly>
```

 This may no longer be needed with the latest build tools but I wanted to mention this because it's important to know that the **Linker** runs before **ProGuard**. So if you have a missing class there's a good chance it's the **Linker's** fault and not **ProGuards** so start there.
 

### Clean your solution after every ProGuard/MultiDex change
If you don't clean your solution, artifacts will remain that cause your build to not truly represent the change you made. Then at some later point your build will act differently and it'll be hard to correlate this to the root cause.


### When deploying I've found the Firebase token becomes invalid on each deployment
I've found that the Firebase token becomes invalid with each build/deploy. So even though the internal Firebase system still retains the first issued token it becomes invalid on the Firebase system so you have to uninstall the app or reset the token. 

### FirebaseApp initialization unsuccessful
I've found Firebase to be really squirrely overall. If you keep getting unsuccessful messages make sure to verify your json file and try deleting all your bin/obj folders and completely removing the app and trying again.




[PureWeen-Repo]: https://github.com/PureWeen/FirebaseSample
[multidex-avoid]: https://developer.android.com/studio/build/multidex.html#avoid
[multidex-limitations]: https://developer.android.com/studio/build/multidex.html#limitations
[multidex-douglas]:http://www.jon-douglas.com/2016/09/05/xamarin-android-multidex/
[xamarin-bug-references]:https://bugzilla.xamarin.com/show_bug.cgi?id=55117
[xamarin-proguard]:https://developer.xamarin.com/guides/android/deployment,_testing,_and_metrics/proguard/#using
[xamarin-proguard-setup]:https://developer.xamarin.com/guides/android/deployment,_testing,_and_metrics/proguard/#customizing
[notepad++]:https://notepad-plus-plus.org/
[VS-DeviceLog]:[https://developer.xamarin.com/guides/android/deployment,_testing,_and_metrics/android_debug_log/]
[xamarin-linker]:https://developer.xamarin.com/guides/cross-platform/advanced/custom_linking
[firebase-docs]:https://firebase.google.com/docs/android/setup#manually_add_firebase