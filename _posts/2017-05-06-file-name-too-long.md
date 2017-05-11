---
title: Path Too Long Exception After Upgrading Google Play Service Xamarin Android
categories: Xamarin Android msbuild
---


`
 System.IO.PathTooLongException: The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters.
` 

 
Tell me more about this specified path please?


In the Android project file you can fix this by setting the following property.


    <IntermediateOutputPath>t</IntermediateOutputPath>

For me just setting it to a single character directory was enough but you could also just use an Absolute path somewhere else.

In my case I just set it under the Release PropertyGroup

```
<PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
    <IntermediateOutputPath>t</IntermediateOutputPath>
```

Or from the command line just use a command line parameter

/p:IntermediateOutputPath:t


This happens from the Xamarin Build task trying to unzip something like this

    obj\Release\__library_projects__\Xamarin.GooglePlayServices.Base\__AndroidLibraryProjects__.zip

Which contains lots of really long xml file names that came from nuget packages.