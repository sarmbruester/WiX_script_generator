# A Windows Installer XML Script Generator

The WiX toolset is a very popular tool to generate installers for .NET applications. It is fairly
easy to set up. However, it requires you to add every single file and directory as relative paths
into its configuration file. This process brings up some issues:

* It is very tiresome to model your file and directory structure if you have a big project with
    hundreds of files
* If your application is changing rapidly, you need to track down every removed/moved/added
    file/directory and change your file, folder and component structure accordingly

WiX toolset provides a way to harvest files with heat.exe. However, in my opinion, that approach
is not very developer friendly.

`make_installer_script.py` aims to ease this process by replicating the file and directory
structure. It is not meant for complete novices at WiX, but if you have some basic knowledge
writing WXS files, it will definitely help. Adapt it to your needs, specifying the

* App name
* App version
* Manufacturer
* Build directory that is to be copied by the installer during the installation process
* Installer directory into which the file `<app name>_<app version>_installer.wxs` will be generated.

Also, provide in the installer directory

* A file `License.rtf` containing the license text for your application
* A file `<app name>.ico` containing the app icon

You may provide empty dummy files for these. After running the Python script, you'll find the WXS
file in the installer directory.
