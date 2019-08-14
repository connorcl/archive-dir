#!/usr/bin/env python3

import argparse
import configparser
from pathlib import Path
import os
import shutil
import platform

platform_os = platform.system()

home_path = Path.home()
data_path = home_path / ".archive-dir"
tmp_path = data_path / "tmp"
config_path = data_path / "config.ini"


class DirectoryToArchive:
	"""Represents a directory to archive, and provides funtions to operate on this directory"""
    
    def __init__(self, path: Path, archive_base_path: Path):
		# directory to archive
        self.path = path
        # base path in which archives are stored
        self.archive_base_path = archive_base_path
        # specific subdirectory in which archive of this directory is stored
        self.specific_archive_path = self.archive_base_path / path.parent.relative_to(home_path)
        # handle fact that Linux creates a tar archive before compressing with 7-Zip
        if platform_os == "Linux":
            archive_file_extension = ".tar.7z"
        elif platform_os == "Windows":
            archive_file_extension = ".7z"
        else:
            raise Exception("Platform not recognised!")
        # path of archive file
        self.archive_file_path = self.specific_archive_path / (self.path.name + archive_file_extension)
        # maps command strings to functions to make calling function based on cli argument easier
        self.commands = {
                "archive": self.archive,
                "verify": self.verify,
                "clean": self.clean_tmp_dir,
                "remove_dir": self.remove_archived_dir,
                "remove_archive": self.remove_archive_file,
                "restore": self.restore_dir
                }
   
    
    def archive(self) -> None:
        """archives the directory"""
        # ensure specific archive path exists
        self.specific_archive_path.mkdir(parents=True, exist_ok=True)
        # ensure specified path exists and archive file does not
        assert self.path.is_dir()
        assert not self.archive_file_path.exists()
        # generate and run command to create and store encrypted archive
        if platform_os == "Linux":
            command = "tar -cf - -C " + "\"" + str(self.path.parent) + "\""
            command += " \"" + self.path.name + "\""
            command += " | 7z a -si -mhe=on -p" + archive_password + " "
            command += "\"" + str(self.archive_file_path) + "\""
        elif platform_os == "Windows":
            command = "7z a -mhe=on -p" + "\"" + archive_password + "\"" + " "
            command += str(self.archive_file_path) + " " + str(self.path)
        else:
            raise Exception("Platform not recognised!")
        print(command)
        os.system(command)
    
    
    def verify(self) -> None:
        """extracts archived directory so its contents can be verified"""
        # ensure both specified directory and corresponding archive file exist
        assert self.path.is_dir()
        assert self.archive_file_path.exists()
        # generate and run commands to extract archive file to tmp directory
        # and compare extracted directory to original directory
        if platform_os == "Linux":
            print("[*] Extracting archive file...")
            command = "7z x -so -p" + archive_password + " " + "\"" + str(self.archive_file_path)
            command += "\"" + " | tar x -C " + "\"" + str(tmp_path) + "\""
            os.system(command)
            print("[*] Using diff to compare original and archived directories...")
            command = "diff -r " + "\"" + str(self.path) + "\"" + " "
            command += "\"" + str(tmp_path / self.path.name) + "\""
            os.system(command)
        elif platform_os == "Windows":
            print("[*] Extracting archive file...")
            command = "7z x -o" + "\"" + str(tmp_path) + "\"" + " -p"
            command += "\"" + archive_password + "\"" + " "
            command += "\"" + str(self.archive_file_path) + "\""
            os.system(command)
            print("[*] Using WinMerge to compare original and archived directories...")
            command = "WinMergeU /r " + "\"" + str(self.path) + "\"" + " "
            command += "\"" + str(tmp_path / self.path.name) + "\""
            os.system(command)
        else:
            raise Exception("Platform not recognised!")
    
    
    def clean_tmp_dir(self) -> None:
        """removes extracted archived directory from tmp directory"""
        print("[*] Removing temporary extracted archive...")
        shutil.rmtree(tmp_path / self.path.name)
    
    
    def remove_archived_dir(self) -> None:
        """prompts to delete a directory that has been archived"""
        # ensure both specified directory and archive file exist
        assert self.path.is_dir()
        assert self.archive_file_path.exists()
        # prompt before deleting directory
        print("[?] Delete archived directory " + str(self.path) + "? [y/N]", end=' ')
        choice = input()
        if choice in ("y", "Y", "yes", "Yes", "YES"):
			# delete archived directory, moving to trash on Linux
            if platform_os == "Linux":
                print("[*] Moving archived directory to trash...")
                command = "gio trash " + "\"" + str(self.path) + "\""
                os.system(command)
            elif platform_os == "Windows":
                print("[*] Deleting archived directory...")
                shutil.rmtree(self.path)
            else:
                raise Exception("Platform not recognised!")
        
        
    def remove_archive_file(self) -> None:
        """prompts to delete an archive file for a directory which is no longer archived"""
        # ensure both specified directory and archive file exist
        assert self.path.is_dir()
        assert self.archive_file_path.exists()
        # prompt before deleting
        print("[?] Delete archive file " + str(self.archive_file_path) + "? [y/N]", end=' ')
        choice = input()
        if choice in ("y", "Y", "yes", "Yes", "YES"):
			# delete archive file, moving to trash on Linux
            if platform_os == "Linux":
                print("[*] Moving archive file to trash...")
                command = "gio trash " + "\"" + str(self.archive_file_path) + "\""
                os.system(command)
            elif platform_os == "Windows":
                print("[*] Deleting archive file...")
                os.remove(self.archive_file_path)
            else:
                raise Exception("Platform not recognised!")
                
        
        
    def restore_dir(self) -> None:
        """restore an archived directory"""
        # ensure archive file exists and specified directory does not
        assert self.archive_file_path.exists()
        assert not self.path.exists()
        # ensure correct directory structure exists in home directory
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # generate command to extract archive into parent of specified directory
        if platform_os == "Linux":
            command = "7z x -so -p" + "\"" + archive_password + "\"" + " " + "\"" + str(self.archive_file_path) + "\""
            command += " | tar x -C " + "\"" + str(self.path.parent) + "\""
        elif platform_os == "Windows":
            command = "7z x -o" + "\"" + str(self.path.parent) + "\"" + " -p"
            command += "\"" + archive_password + "\"" + " "
            command += "\"" + str(self.archive_file_path) + "\""
        else:
            raise Exception("Platform not recognised!")
        os.system(command)
        
        
    def run_command(self, command: str):
        self.commands[command]()


def process_path(path: Path, must_be_absolute: bool = False) -> Path:
    """resolves home path shorthand (~) and ensures path is absolute"""
    if path.parts[0] == "~":
        path = home_path / path.relative_to("~")
    if must_be_absolute:
        assert path.is_absolute()
    return path.absolute()


def setup_program_dirs() -> None:
    """ensures the correct program directories are in place"""
    data_path.mkdir(exist_ok=True)
    tmp_path.mkdir(exist_ok=True)
    

def parse_config() -> dict:
    """ensure config file is present and valid and parses it"""
    config = configparser.ConfigParser()
    # if config file is not present, create one with blank values
    if not config_path.exists():
        config['DEFAULT'] = {
            "archive_base_path": "",
            "archive_password": ""
        }
        with open(data_path / "config.ini", 'w') as config_file:
            config.write(config_file)
    config.read(config_path)
    # ensure no values are blank
    if "" in config['DEFAULT'].values():
        raise Exception("Please specify valid configuration in config file " + str(config_path))
    else:
        return config['DEFAULT']
    
    
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Handles the archiving of user directories")
    parser.add_argument("command", help="archive, verify, clean, remove_dir, remove_archive or restore")
    parser.add_argument("path", help="""directory on which command operates. 
                    For restore and remove_archive, this should be the path which was 
                    initially archived, not the location of the archive file""")
    return parser.parse_args()
    

def main() -> None:
    setup_program_dirs()
    config = parse_config()
    global archive_password
    archive_password = config['archive_password']
    args = parse_arguments()
    dir_to_archive = DirectoryToArchive(process_path(Path(args.path)), 
										 process_path(Path(config['archive_base_path']), True))
    dir_to_archive.run_command(args.command)

if __name__ == "__main__":
    main()
