--- 
title:  "Xamarin Forms Debugging Tips"
date:   2018-02-01 00:00:00 -0600
categories: Xamarin Forms Debugging
comments: true
---

### Stepping through Xamarin.Forms source code
- Life is easiest if you can clone to the d drive
    - *git clone https://github.com/xamarin/Xamarin.Forms.git d:\a\1\s*
- If you don't have a D drive then you can use *subst*
    - *git clone https://github.com/xamarin/Xamarin.Forms.git c:\SomeFolder\a\1\s*
    - subst d: c:\SomeFolder
        - If you get a parameter error message it means the D drive is being used by something else
- Identify the tag/commit of the nuget package
    - Tag Method
        - If you go to [Xamarin Forms](https://github.com/xamarin/Xamarin.Forms) on GitHub, you will notice that the Forms tags have a consistent naming scheme
            - RC is the initial release and SR marks each additional release. For example *release-3.4.0-sr2* applies to *3.4.0.1029999*
        - git checkout tags/release-3.4.0-sr2
    - Commit Method
        - [Forms Releases](https://github.com/xamarin/Xamarin.Forms/releases) lists the commits associated with each release
        - git checkout 588023e
- Now you're ready to step into the source code. Run your project and when you try to step into anything or view the call stack it'll let you navigate to the files at *d:/a/1/s*

### Working on a fix you want to submit?
- The [Control Gallery](https://github.com/xamarin/Xamarin.Forms/tree/master/Xamarin.Forms.ControlGallery.Android) projects that are part of the main solution are a great place to setup and test your scenarios from.
    - The main page is loaded from the following [CreateDefaultMainPage](https://github.com/xamarin/Xamarin.Forms/blob/78385f9fc1fc56dc88bd98e73bf9c8f2f2d0a90a/Xamarin.Forms.Controls/App.cs#L107) method. 
    - If you submit a fix you'll most likely need to add an issue [here](https://github.com/xamarin/Xamarin.Forms/tree/78385f9fc1fc56dc88bd98e73bf9c8f2f2d0a90a/Xamarin.Forms.Controls.Issues/Xamarin.Forms.Controls.Issues.Shared) which gets loaded into the Control Gallery test runner.
    - Typically when I'm developing fixes I'll start with loading my test cases inside the [CreateDefaultMainPage](https://github.com/xamarin/Xamarin.Forms/blob/78385f9fc1fc56dc88bd98e73bf9c8f2f2d0a90a/Xamarin.Forms.Controls/App.cs#L107) method and then once I've reproduced and fixed the issue I move it over to an official UI test issue.

### Compiling Issues
- On windows everything should compile without needing to do anything
    - if you are getting errors try running *git clean -xdf*. Sometimes left over files from changing branches can cause issues
- Current issues with multi targeting make VS Mac a bit trickier to work with.
    - Here's a [Gist](https://gist.github.com/PureWeen/92c1e1aff0c257c3decf0bcb8d6e9296) for a script you can use


### Source Link
- Currently the Xamarin Debugger doesn't support SourceLink style debugging. The internal wheels are turning on this and once it is ready Forms will add SourceLink support

### Build scripts
- Currently working on build scripts to help with nuget packaging and different build scenarios (https://github.com/xamarin/Xamarin.Forms/pull/5074)