

Tell me more about this specified path please?


 System.IO.PathTooLongException: The specified path, file name, or both are too long. The fully qualified file name must be less than 260 characters, and the directory name must be less than 248 characters.
    
 


Fix by setting

    <IntermediateOutputPath>t</IntermediateOutputPath>

To some path (relative or absolute) that won't exceed the Windows minimums. 

or passing in an msbuild parameter
/p:IntermediateOutputPath:t

This happens from the Xamarin Build task trying to unzip something like

    obj\Release\__library_projects__\Xamarin.GooglePlayServices.Base\__AndroidLibraryProjects__.zip

Which contains lots of really long xml file names that came from nuget package.