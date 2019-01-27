--- 
title:  "Xamarin Forms Debugging Tips"
date:   2018-02-01 00:00:00 -0600
categories: Xamarin Forms Debugging
comments: true
---

### Setting up the source code
- Life is easiest if you can clone do the d drive
    - *git clone https://github.com/xamarin/Xamarin.Forms.git d:\a\1\s*
- If you don't have a D drive then you can use *subst*
    - *git clone https://github.com/xamarin/Xamarin.Forms.git c:\SomeFolder\a\1\s*
    - subst d: c:\SomeFolder
        - If you get a parameter error message it means the D drive is being used by something else
- Identify the tag/commit of the nuget package
    - Tag Method
        - If you go to Xamarin Forms on github you will notice that the Forms tags have a consistent naming scheme
            - RC is the initial release and SR marks each additional release
                - For example *release-3.4.0-sr2* applies to *3.4.0.1029999*
    - Commit Method
        - https://github.com/xamarin/Xamarin.Forms/releases lists the commits associated with each release
        - git checkout 588023e
- Once you've identified the tag for the nuget release
    - git checkout tags/release-3.4.0-sr2

### Source Link
- Currently the Xamarin Debugger doesn't support SourceLink style debugging. The internal wheels are turning on this and once it is ready Forms will add SourceLink support

### Build scripts
- Currently working on build scripts to help with nuget packaging (https://github.com/xamarin/Xamarin.Forms/pull/5074)