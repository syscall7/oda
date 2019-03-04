## About Online DisAssembler (ODA)

ODA (onlinedisassembler.com) is a reverse engineering platform that provides a
collaborative reversing experience hosted in the cloud.  With ODA, groups of
people can collaborate on reversing the same binary and share their
contributions in real time.  ODA seeks to become “GitHub and Google Docs meets
IDA Pro”.

## ODA Documentation

The latest documentation for the ODA project can be found
[here](https://onlinedisassembler.com/doc).

## Using ODA

The typical workflow is to upload a file via the "File->Upload File" menu.
Once the file has been loaded, a user can begin to markup and annotate the
disassembly through right-click context menus as well as keyboard shortcuts.

Collaboration requires signing into ODA with a username and password.

## Getting Help with ODA

If you have any questions about, feedback for or a problem with ODA:

* Ask a question on the [Mailing List](https://groups.google.com/a/syscall7.com/forum/#!forum/oda)
* [Open an Issue](https://github.com/syscall7/oda/issues/new)

## Contributing to ODA

Please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

## Known Limitations

* Setting the ENDIAN option in Live View and File Upload does not work
* Cannot delete structure definitions
* Structure definitions do not support pointer types
* Converting data to code does not recusively follow newly found functions
* Creating structure definitions can only be triggered through a keyboard shortcut
* Nested structure definitions are not fully supported
* The links in the Sections Tab do not navigate to the corresponding address
* The link to Live View does not work, but you can get to it through the
  strcpy example
* Keyboard shortcuts only work if you have focus in the disassembly window
* File uploads are currently limited to 2.5 MB (can be changed)
* Downloading disassembly listing does not work
* Registering for an account currently throws an exception, but if you sign in
  with the credentials given, you can still get to your account.

## Future Work

* IDA Integration (import/export IDB files)
* Python scripting interface
* User and group management
  * Integrating with PKI-based authentication systems
  * Easily share binaries between users in same group
* Analytics
  * Draw from a corpus of previously reversed samples
  * Enhance integration of runtime analysis
  * Automatic import table reconstruction
  * Enhance dissection of Windows executables
  * Improve data types (i.e., strings)

## Docker Installation (ubuntu)

```$bash
sudo apt-get update

sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
   
sudo apt-get update   

sudo apt-get install -y docker-ce

sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

```
