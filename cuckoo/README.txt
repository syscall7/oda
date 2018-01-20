
Installing Cuckoo with ODA Modifications
========================================

1. Get the Cuckoo source

You'll need to download two Cuckoo repositories: a) the main Cuckoo repo, and b) the Cuckoo monitor DLL repo.

  # create your cuckoo directory
  mkdir ~/cuckoo_sandbox
  cd ~/cuckoo_sandbox

  # cuckoo main
  git clone https://github.com/cuckoobox/cuckoo
  pushd cuckoo
  git checkout -q 239fb440b05038d0016cb416bc1c1768a0870100
  popd

  # cuckoo monitor DLL (not necessary if using pre-built ODA Cuckoo DLL)
  git clone https://github.com/cuckoobox/cuckoomon.git
  pushd cuckoomon
  git checkout -q cccba1ae19755ab5e45327a9683d230897269e41
  popd

2. Apply the ODA patches

  # Get the Cuckoo patches
  cd ~/cuckoo_sandbox
  svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/cuckoo/patches

  # apply the analyzer patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < ../patches/analyzer.patch
  popd

  # apply the REST API patch
  pushd ~/cuckoo_sandbox/cuckoo
  patch --verbose -u -p1 < ../patches/rest_api.patch
  popd

  # apply the cuckoo monitor DLL patch
  # NOTE: Not necessary if using pre-built ODA Cuckoo DLL
  pushd ~/cuckoo_sandbox/cuckoomon
  patch --verbose -u -p1 < ../patches/cuckoomon.patch
  popd

3. Build the Cuckoo monitor DLL

  NOTE: You can skip this step by using ODA's pre-built version of
        cuckoomon.dll.  You can check it out here:

        svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/cuckoo/cuckoomon.dll

  To build from source, you'll first have to install a mingw environment:
      sudo apt-get install mingw32

  Next, build the DLL:
      pushd ~/cuckoo_sandbox/cuckoomon
      make

4. Move the Cuckoo monitor DLL into Cuckoo

  The ODA cuckoomon.dll file (either the ODA pre-built version or the one you
  just built) needs to be moved into cuckoo.

    cp cuckoomon.dll ~/cuckoo_sandbox/cuckoo/analyzer/windows/dll/cuckoomon.dll

5. Install Cuckoo dependencies

  virtualenv cuckoo_python_env
  source cuckoo_python_env/bin/activate
  pip install -r requirements.txt

6. Install VirtualBox

  See the VirtualBox website for installation instructions on your host.

  On Ubuntu, you can install virtualbox with:
    
    sudo apt-get install virtualbox

7. Get the VM image

  Grab and extract a copy of the Windows XP VM:
    
    # Download the Windows XP VM from my Google Drive
    https://drive.google.com/a/ransomed.us/file/d/0B6vDgWy-q6Dxc2s0NHB3Z2NGNTA/edit?usp=sharing

    # Extract the image
    cd ~/cuckoo_sandbox
    tar -xJf windows_xp_cuckoo_vm.tar.xz

8 (Headless) . Virtual Box Networking
	
    sudo VBoxManage hostonlyif create
    VBoxManage registervm ~/cuckoo_sandbox/windows_xp_cuckoo_vm/windows_xp_cuckoo_vm.vbox

8 (GUI). Add the VM image to VirtualBox

  Start VirtualBox and add the Windows XP VM:
 
    Create a host network

    sudo virtualbox
    Click Machine->Add and navigate to the XP VM image.
    Close VirtualBox

9. Configure Cuckoo

  Edit ~/cuckoo_sandbox/cuckoo/conf/cuckoo.conf with the following changes:
    
    # Under the [timeouts] section set the default timeout
    default = 10

  Edit ~/cuckoo_sandbox/cuckoo/conf/virtualbox.conf with the following changes:

    # Under the [virtualbox] section
    mode = headless

    # Under the [cuckoo1] section
    label = windows_xp_cuckoo_vm

    # Our Windows XP VM has a snapshot named Snapshot1
    snapshot = Snapshot1


Running Cuckoo
================

Running Cuckoo involves starting the main Cuckoo server as well as the REST
API server.

To start the main Cuckoo server:

  cd ~/cuckoo_sandbox/cuckoo
  sudo ./cuckoo -d

To start the Cuckoo API server in another terminal:

  cd ~/cuckoo_sandbox/cuckoo
  sudo ./utils/api.py

To submit a new job:

  # Checkout some Win32 example programs
  svn co svn://svn.onlinedisassembler.com/oda/ODA/trunk/cuckoo/samples

  # Submit a job
  sudo ./utils/submit.py --package exe --options procmemdump=yes ./samples/ipconfig.exe

  # Look for memory dump output (you should see a file called <pid>.dmp)
  ls ~/cuckoo_sandbox/cuckoo/storage/analyses/latest/memory/

  
