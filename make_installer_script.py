
"""
Generates a Windows Installer XML (WiX) script for a given build directory into an existing installer directory.
Within the installer directory, there is a license text expected in the file License.rtf and an app icon in the
file <app_name>.ico.
"""

import os
import uuid
from typing import IO, Tuple, List


def slash_join(*args) -> str:
    """
    Builds a path from args that uses slashes as separators exclusively.
    Especially useful for displaying paths or checking their equality.
    """
    converted = [i.replace('\\', '/').strip('/') for i in args]
    return '/'.join(converted)


def get_dir_tails(dp1: str, dp2: str) -> Tuple[List[str], List[str]]:
    """
    For each of two directory paths, returns a list of trailing directories after a common root path.
    The two directory paths are expected to have slashes as separators only.
    """
    dp1split = dp1.split('/')
    dp2split = dp2.split('/')
    for i in range(max(len(dp1split), len(dp2split))):
        if i == len(dp1split):
            return [], dp2split[i:]
        elif i == len(dp2split):
            return dp1split[i:], []
        elif dp1split[i] != dp2split[i]:
            return dp1split[i:], dp2split[i:]


# adapt configuration as needed
app_name = 'app_name'
app_version = '0.0.42'
manufacturer = 'Acme Corporation'
build_dir = './build'
installer_dir = './installer'
installer_path = slash_join(installer_dir, f'{app_name}_{app_version}_installer.wxs')
indent = ' ' * 4
components = ['MainExecutable']


def do_part_1(f: IO) -> None:
    f.write(f'''<?xml version='1.0' encoding='windows-1252'?>
<Wix xmlns='http://schemas.microsoft.com/wix/2006/wi'>
    <?define AppName = "{app_name}"?>
	<?define AppVersion = "{app_version}"?>
	<?define FullAppName = "$(var.AppName) $(var.AppVersion)"?>
    <?define BuildDir = "{build_dir}"?>
	<Product Name='$(var.FullAppName)' Manufacturer='{manufacturer}'
			Id='D74B625D-BD2B-48E8-9095-498A1B4755B4'
			UpgradeCode='292360CB-7605-4567-9FA0-99490FA71BC0'
			Language='1033' Codepage='1252' Version='$(var.AppVersion)'>
		<Package Id='*' Keywords='Installer' Description="$(var.FullAppName) Installer"
			Comments='comment like "{app_name} is a registered trademark of {manufacturer}"'
			Manufacturer='{manufacturer}'
			InstallerVersion='100' Languages='1033' Compressed='yes' SummaryCodepage='1252' />
		<Media Id='1' Cabinet='{app_name}.cab' EmbedCab='yes' />
		<Property Id="WIXUI_INSTALLDIR" Value="INSTALLDIR" />
        <UIRef Id="WixUI_InstallDir" />
        <UIRef Id="WixUI_ErrorProgressText" />
        <WixVariable Id="WixUILicenseRtf" Value="License.rtf" />
		<Directory Id='TARGETDIR' Name='SourceDir'>
		    <Directory Id='ProgramFilesFolder'>
		        <Directory Id='{manufacturer}' Name='{manufacturer}'>
                    <Directory Id='INSTALLDIR' Name='$(var.FullAppName)'>
                        <Component Id='{components[0]}' Guid='8D469269-11D2-4945-8BF1-AE2AF5047C35'>
                            <File Id='{app_name}.exe' Source='$(var.BuildDir)/{app_name}.exe' KeyPath='yes'>
                                <Shortcut Id="startmenu_{app_name}" Directory="ProgramMenuDir" Name='$(var.FullAppName)'
                                    WorkingDirectory='INSTALLDIR' Icon="{app_name}.ico" IconIndex="0" Advertise="yes" />
                                <Shortcut Id="desktop_{app_name}" Directory="DesktopFolder" Name='$(var.FullAppName)'
                                    WorkingDirectory='INSTALLDIR' Icon="{app_name}.ico" IconIndex="0" Advertise="yes" />
                            </File>
                        </Component>\n''')


def do_part_2(f: IO) -> None:
    depth = 6
    walker = os.walk(build_dir)
    c_idx = 0
    d_idx = 0

    # write all files in the main folder except <app_name>.exe
    top_level_files = next(walker)[-1]
    for i in top_level_files:
        if i != f'{app_name}.exe':
            c_idx += 1
            c_id = f'component_{c_idx}'
            c = slash_join(build_dir, i)
            f.write(f"{indent * depth}<Component Id='{c_id}' Guid='{uuid.uuid4()}'>\n"
                    f"{indent * (depth + 1)}<File Id='{c_id}' Source='{c}' KeyPath='yes' Checksum='yes'/>\n"
                    f"{indent * depth}</Component>\n")
            components.append(c_id)

    # write all subdirectories
    previous_dirpath = build_dir
    for dp, _, filenames in walker:
        # if current subdir merely contains directories but no files, we don't do anything
        if not filenames:
            continue
        # we are going to change into the current directory
        # as dirpath separators, we want slashes only
        dirpath = slash_join(dp)
        tail1, tail2 = get_dir_tails(previous_dirpath, dirpath)
        # navigate up
        for _ in range(len(tail1)):
            depth -= 1
            f.write(f'{indent * depth}</Directory>\n')
        # navigate down
        for i in range(len(tail2)):
            d_idx += 1
            f.write(f"{indent * depth}<Directory Id='directory_{d_idx}' Name='{tail2[i]}'>\n")
            depth += 1

        # write components
        for i in filenames:
            c_idx += 1
            c_id = f'component_{c_idx}'
            c = slash_join(dirpath, i)
            f.write(f"{indent * depth}<Component Id='{c_id}' Guid='{uuid.uuid4()}'>\n"
                    f"{indent * (depth + 1)}<File Id='{c_id}' Source='{c}' KeyPath='yes' Checksum='yes'/>\n"
                    f"{indent * depth}</Component>\n")
            components.append(c_id)

        previous_dirpath = dirpath

    # add closing tags
    tail1, _ = get_dir_tails(previous_dirpath, build_dir)
    for _ in range(len(tail1) + 1):
        depth -= 1
        f.write(f'{indent * depth}</Directory>\n')

    components.append('ProgramMenuDir')


def do_part_3(f: IO) -> None:
    f.write(f'''                </Directory>
			</Directory>
			<Directory Id="ProgramMenuFolder" Name="Programs">
                <Directory Id="ProgramMenuDir" Name='$(var.FullAppName)'>
                    <Component Id="ProgramMenuDir" Guid="2A4E1D9D-26AF-4938-9126-774756326C90">
                        <RemoveFolder Id='ProgramMenuDir' On='uninstall' />
                        <RegistryValue Root='HKCU' Key='Software\[Manufacturer]\[ProductName]' Type='string'
                            Value='' KeyPath='yes' />
                    </Component>
                </Directory>
            </Directory>
            <Directory Id="DesktopFolder" Name="Desktop" />
		</Directory>\n''')


def do_part_4(f: IO) -> None:
    f.write('''        <Feature Id='Complete' Title='$(var.FullAppName)' Description='The complete package.'
                Display='expand' Level='1' ConfigurableDirectory='INSTALLDIR'>\n''')
    [f.write(f"{indent * 3}<ComponentRef Id='{i}' />\n") for i in components]
    f.write(f'''        </Feature>
        <Icon Id="{app_name}.ico" SourceFile="{app_name}.ico" />
    </Product>
</Wix>\n''')


def main() -> None:
    with open(installer_path, 'w') as f:
        do_part_1(f)
        do_part_2(f)
        do_part_3(f)
        do_part_4(f)


if __name__ == '__main__':
    main()
