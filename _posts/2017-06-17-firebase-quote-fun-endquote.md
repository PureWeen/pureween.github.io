--- 
title:  "Fun with Firebase, references, proguard, and multidex"
date:   2017-05-07 19:58:16 -0600
categories: Task Rx.NET
---


So you've read the examples, installed the libraries, copied over the samples and now you're ready for some firey messaging magic. 

```
error MSB6006: "java.exe" exited with code 2. // :-(
```

Checking the build logs yield nothing of value unless you increae the logging detail (insert pretty link here)


```
2>  trouble writing output: Too many field references to fit in one dex file: 68555; max is 65536. (TaskId:349)
2>  You may try using multi-dex. If multi-dex is enabled then the list of classes for the main dex list is too large. (TaskId:349)
2>  References by package: (TaskId:349)
```

Unfortunately you can hit this limit fairly fast with the latest and greatest Xamarin Support libraries.   The error above came from a brand new project with what I would consider a basic set of 3rd party libraries.

HockeyApp, Xamarin.FireBase, Xamarin.Forms, Xamarin.Forms.Maps, Azure Messaging


Looking at the list of references used up you can see a large number are straight from support libraries and it doesn't leave much room for your own.

Solutions multidex and proguard

In this post I'll mainly focus on Proguard as it's the preferred solution before going with multidex.
https://developer.android.com/studio/build/multidex.html#avoid
https://developer.android.com/studio/build/multidex.html#limitations


MultiDex 

This solution isn't too hard to get working. The main issue you'll run into here is when compiling with windows and wanting your app to run on pre-lollipop

http://www.jon-douglas.com/2016/09/05/xamarin-android-multidex/

Once you're able to generate a multidex.keep file you can copy that into your project and modify as needed


https://bugzilla.xamarin.com/show_bug.cgi?id=44187
https://bugzilla.xamarin.com/show_bug.cgi?id=55268






Proguard
In order for ProGuard to run the linker has to be enabled. I've found that I can have to run in Debug will Full linking (Sdk and User assemblines) on in order for it to compile.
https://developer.xamarin.com/guides/android/deployment,_testing,_and_metrics/proguard/#using
This bug as well might alleviate most of the pains
https://bugzilla.xamarin.com/show_bug.cgi?id=55117


Enable proguard and magically it should all work?

```
error MSB6006: "java.exe" exited with code 1.
```

That's better than code 2 right? It's one closer to zero so we must be on the right track :-x

Because our build logging is still set to "Detailed" (unless you started here in which case go set your build output to Detailed) we can check the output and  see a bunch of warnings and PROGUARD messages.. Here's a snippet

```
warning : com.google.firebase.messaging.zzc: can't find referenced class com.google.android.gms.measurement.AppMeasurement
...

java.io.IOException: Please correct the above warnings first.
2>  	at proguard.Initializer.execute(Unknown Source)
2>  	at proguard.ProGuard.initialize(Unknown Source)
2>  	at proguard.ProGuard.execute(Unknown Source)
2>  	at proguard.ProGuard.main(Unknown Source)
```


Much like a linker file we're going to need to setup a proguard configuration file to help PROGUARD out.  Through some trial and error this is what I ended up with for my proguard.cfg file

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

Only the first two gms lines were needed for it to compile the rest of it thought was needed so the app wouldn't crash and complain about missing classes. This file could probably be refined a little bit to be more specific of what needs to be kept but for now I've found that this worked for me.

Add these into a proguard file and set the buid action to ProGuardconfiguration

More info here on how to add the file
https://developer.xamarin.com/guides/android/deployment,_testing,_and_metrics/proguard/#customizing


Alright now we have a proguard file and we're good to go. Click compile

```
error MSB6006: "java.exe" exited with code 1. //:-(

1>  proguard.ParseException: Unknown option '∩╗┐-keep' in line 1 of file 'proguard.cfg',
1>    included from argument number 10
1>  	at proguard.ConfigurationParser.parse(Unknown Source)
1>  	at proguard.ProGuard.main(Unknown Source)
```

If you google the exception there are a ton of resources talking about how to fix.  
https://stackoverflow.com/questions/38743557/xamarin-proguard-parseexception-unknown-option-in-line-1-of-file-properties

Basically you need to encode the file in UTF-8  Without BOM. I tried a few solutions and plugins from VS but the only thing I was able to get working was to use Notepad++ to save the file

Just open it up in Notepad++ and set the Encoding

```
Encoding > Encode in UTF-8
```

Then re-save the file and try to compile again

It compiles!!!!!!!!!!!!!!!!!!!!

Alright now let's run the application in real life to see what happens.

If we check the device log via Visual Studio or Android Studio we see an exception


Here's the part where it's going to depend a little bit on your specific project in order to get these settings all correct for your Proguard file.  In my case I was able to get the code to compile with only these lines

```
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.android.gms.**
```

But then I needed these additional ones 
```
-keep class com.microsoft.windowsazure.messaging.** { *; }
-dontwarn com.microsoft.windowsazure.messaging.**
-keep class com.google.firebase.** { *; }
-dontwarn com.google.firebase.**
-keep class android.support.v7.widget.** { *; }
-dontwarn android.support.v7.widget.**
-keep class android.support.v4.widget.Space { *; }
-dontwarn android.support.v4.widget.Space
```

in order for the app to not crash and throw exceptions like "blankity blank class not found"

```
Caused by: java.lang.ClassNotFoundException: Didn't find class "android.support.v7.widget.FitWindowsFrameLayout"
```

My recommendation after getting ProGuard setup would be to click around everywhere in your app and watch the device logs for any class not found exceptions that you'll need to resolve. 


At this point you can hopefully run your app and see this message in your device logs

```
FirebaseApp initialization successful
```

Side note. Firebase log messages are a lot harder to find when you named your project firebase :-/
 

For the Firebase Fun project I was able to get firebase working without having to worry about the Linker but when I initially did this for my own personal project I had to setup a linker file for the FirebaseInitProvider.  This may no longer be needed with the latest build tools but I want to mention it because it's important to know that the Linker runs before Proguard.  Therefore if you're getting a missing class exception it might be getting linked away and have nothing to do with Proguard.   Here's a really great article going more in depth on that one http://www.jon-douglas.com/2016/09/05/xamarin-android-multidex/

The error I was seeing was unable to find
```
com.google.firebase.provider.FirebaseInitProvider
```

I was able to resolve this by adding this to my Linker.xml file

``` 
<assembly fullname="Xamarin.Firebase.Common">
    <type fullname="Firebase.Provider.FirebaseInitProvider" />
 </assembly>

```

More on setting up this file can be found here https://developer.xamarin.com/guides/cross-platform/advanced/custom_linking/

Again this may not be necessary but I felt it important to mention so that you don't get stuck thinking Proguard is stripping away your classes but in fact it's the Linker.



Some general notes
If you change a multidex or proguard setting clean your solution (maybe even just delete all obj and bin). Otherwise things stick around that don't represent reality

I've found that the firebase token becomes invalid with each build. So even though the internal firebase system still retains the first issued token it becomes invalid on the firebase system so you have to uninstall the app or reset the token