# archive-dir
A simple Python script to archive and restore directories on Linux and Windows

## Dependencies

On both systems, Python (version 3) must be installed to run this script. It has been tested using version 3.7.

On Linux, this script depends on `p7zip` and `diffutils`, which can be installed using most Linux distributions' package managers. `7z` and `diff` must be in the system `PATH` for the script to run successfully.

On Windows, the script depends on [7-Zip](https://www.7-zip.org) and [WinMerge](https://winmerge.org). `7z` and `WinMergeU` must be in the system `PATH` for the script to run successfully.

## Usage

When the script is first run, it will create the directory `.archive-dir` in the user's home directory. Within this directory, it will initialize its config file, `config.ini`. This config file defines the archive encryption password and the base directory in which archives will be stored. These settings must be specified by the user before any of the functionality of the script can be carried out.

The script can then be run with two arguments, a command and a directory, as follows:

```
python archive-dir.py command /directory/to/archive
```

A number of commands are accepted. Note that the path to specify is always that of the directory to archive (or which has previously been archived), even if this original directory has been removed.

`archive` will create an encrypted archive of the specified directory and store it under the archive base directory. The parent directory structure of the archived directory (up to the user's home directory) is recreated under the archive base path, so that, for example, if the directory `/home/user/foo/bar` was archived under the archive base path `/home/user/archive`, the archive file would be stored in the directory `/home/user/archive/foo`. This allows archive files to remain organised.

`verify` will extract a created archive into `.archive-dir/tmp` and compare it to the original directory using `diff` on Linux and WinMerge on Windows.

`clean` will delete the extracted archive from `.archive-dir/tmp`.

`remove_dir` will remove a directory which has been archived. This will not remove a directory which has not been archived, but be sure to `verify` created archives before using this command.

`remove_archive` will remove an archive file. This will not remove an archive file whose corresponding original directory is not present, but be sure to check the contents of the original directory are valid before using this command.

`restore` will extract an archived directory and restore it to its original location in the user's home directory.
