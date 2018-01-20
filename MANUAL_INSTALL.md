## ODA Manual Installation

#### Dependencies

ODA requires the following dependencies:

* Ubuntu 16.04 LTS
* Apache
* MySQL
* Python 2.7
* Node.js
* Binutils Source Code (binutils-2.24.51.tar.bz2)
* libxml2-dev
* libxslt1-dev
* git
* texinfo
* patch
* bzip2
* gcc
* make
* autoconf
* python-pip
* python-virtualenv
* libpython-dev
* libssl-dev
* libffi-dev
* cython
* libapache2-mod-wsgi
* libmysqlclient-dev
* The following Python modules are required for the ODA server:
  * Cython==0.20.1
  * Django==1.8.6
  * MySQL-python==1.2.5
  * argparse==1.2.1
  * django-allauth==0.18.0
  * django-appconf==0.6
  * django-compressor==1.4
  * djangorestframework==2.3.13
  * dnspython==1.11.1
  * nose==1.3.1
  * oauthlib==0.6.1
  * python-openid==2.2.5
  * requests==2.2.1
  * requests-oauthlib==0.4.0
  * six==1.6.1
  * wsgiref==0.1.2
  * gsutil==3.42
  * django-google-storage==0.3
  * bidict==0.1.5
  * ipython==2.2.0
  * beautifulsoup4==4.3.2
  * lxml==3.4.0

#### Installing Django core application

Ensure the dependencies are installed before proceeding.

```bash
ODA_SRC_DIR=/home/<user>
ODA_INSTALL_DIR=/var/www/oda
```

Create some ODA directories:
```bash
sudo mkdir -p /var/oda/uploads
sudo mkdir -p /var/oda/cache
sudo mkdir -p /tmp/cache
sudo chown -R www-data.www-data /var/oda /tmp/cache
```

Setup the python virtual environment:
```bash
sudo mkdir $ODA_INSTALL_DIR
sudo virtualenv $ODA_INSTALL_DIR/env
```

Build and install our custom version of the BFD library:
```bash
cd $ODA_SRC_DIR/bfd
sudo ./build_bfd.sh
```

Copy the ODA source code to the WWW directory and install the Python requirements:
```bash
sudo mkdir $ODA_INSTALL_DIR/site
cd $ODA_INSTALL_DIR/site/
sudo cp -R $ODA_SRC_DIR/django/* .
sudo $ODA_INSTALL_DIR/env/bin/pip install -r requirements.txt
sudo chown -R www-data $ODA_INSTALL_DIR
sudo chgrp -R www-data $ODA_INSTALL_DIR
```

Build the ODA BFD python module:
```bash
cd $ODA_SRC_DIR/bfd
sudo $ODA_INSTALL_DIR/env/bin/python setup.py install
```
#### Installing NodeJS

NodeJS is used for websocket-based notifications to users:
```bash
curl -sL https://deb.nodesource.com/setup | sudo bash -
sudo apt-get install nodejs
cd $ODA_SRC_DIR/nodejs
npm install
```

#### Installing MySQL

Install MySQL packages and set a default `root` password:
```bash
export ODA_MYSQL_PASSWORD=somepassword
echo mysql-server mysql-server/root_password password "$ODA_MYSQL_PASSWORD" | sudo debconf-set-selections
echo mysql-server mysql-server/root_password_again password "$ODA_MYSQL_PASSWORD" | sudo debconf-set-selections
sudo apt-get install mysql-server libmysqlclient-dev -y
```

#### Configure ODA database
```bash
export ODA_MYSQL_DATABASE=odapython3
export ODA_MYSQL_USER=root
cd $ODA_SRC_DIR/django
echo "create database odapython3;" | mysql --user=root --password="$ODA_MYSQL_PASSWORD"
sudo -E $ODA_INSTALL_DIR/env/bin/python manage.py migrate --settings=oda.settings.development
sudo -E $ODA_INSTALL_DIR/env/bin/python manage.py setup_oda --settings=oda.settings.development
sudo -E $ODA_INSTALL_DIR/env/bin/python manage.py setup_openid --settings=oda.settings.development
```

#### Installing Apache VirtualHost Site

Fixup the wsgi script to point to our install location:
```bash
perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $ODA_INSTALL_DIR/site/oda.wsgi  > $ODA_INSTALL_DIR/site/oda.wsgi_2
mv $ODA_INSTALL_DIR/site/oda.wsgi_2 $ODA_INSTALL_DIR/site/oda.wsgi
perl -p -i -e 's/\$\{([^}]+)\}/defined $ENV{$1} ? $ENV{$1} : $&/eg' < $ODA_INSTALL_DIR/site/apache_odaweb.site > $ODA_INSTALL_DIR/site/onlinedisassembler.conf
mv $ODA_INSTALL_DIR/site/onlinedisassembler.conf /etc/apache2/sites-available/
```

#### Install Cuckoo with ODA modifications

NOTE: This is still an alpha feature and considered a prototype.

##### Get the Cuckoo source

You'll need to download two Cuckoo repositories: a) the main Cuckoo repo, and b) the Cuckoo monitor DLL repo.

Create your cuckoo directory:
```bash
mkdir ~/cuckoo_sandbox
cd ~/cuckoo_sandbox
```

Download Cuckoo main:
```bash
git clone https://github.com/cuckoobox/cuckoo
pushd cuckoo
git checkout -q 239fb440b05038d0016cb416bc1c1768a0870100
popd
```

Download Cuckoo monitor DLL (not necessary if using pre-built ODA Cuckoo DLL)
```bash
git clone https://github.com/cuckoobox/cuckoomon.git
pushd cuckoomon
git checkout -q cccba1ae19755ab5e45327a9683d230897269e41
popd
```

##### Apply the ODA patches

Get the Cuckoo patches:
```bash
cd ~/cuckoo_sandbox
cp -r $ODA_SRC_DIR/cuckoo/patches .
```

Apply the analyzer patch:
```bash
pushd ~/cuckoo_sandbox/cuckoo
patch --verbose -u -p1 < ../patches/analyzer.patch
popd
```

Apply the REST API patch:
```bash
pushd ~/cuckoo_sandbox/cuckoo
patch --verbose -u -p1 < ../patches/rest_api.patch
popd
```

Apply the cuckoo monitor DLL patch (not necessary if using pre-built ODA Cuckoo DLL)
```bash
pushd ~/cuckoo_sandbox/cuckoomon
patch --verbose -u -p1 < ../patches/cuckoomon.patch
popd
```

##### Build the Cuckoo monitor DLL

NOTE: You can skip this step by using ODA's pre-built version of cuckoomon.dll
($ODA_SRC_DIR/cuckoo/cuckoomon.dll)

To build from source, you'll first have to install a mingw environment: 
```bash
sudo apt-get install mingw32
```

Next, build the DLL:
```
pushd ~/cuckoo_sandbox/cuckoomon
make
```

##### Move the Cuckoo monitor DLL into Cuckoo

The ODA cuckoomon.dll file (either the ODA pre-built version or the one you
just built) needs to be moved into cuckoo.

```bash
cp cuckoomon.dll ~/cuckoo_sandbox/cuckoo/analyzer/windows/dll/cuckoomon.dll
```

##### Install Cuckoo dependencies

```bash
virtualenv cuckoo_python_env
source cuckoo_python_env/bin/activate
pip install -r requirements.txt
```

##### Install VirtualBox

See the VirtualBox website for installation instructions on your host.  On
Ubuntu, you can install virtualbox with:
```bash
sudo apt-get install virtualbox
```

##### Setup a Windows XP VM image

Setup a Windows XP VM image in virtual box and configure it for Cuckoo.  See
http://cuckoo.readthedocs.org/en/latest/installation/guest/

Name the VM image windows_xp_cuckoo_vm to match the 'label' option in
cuckoo/virtualbox.conf.

##### Configure the VM's networking options

In VirtualBox GUI:
1. Add the VM image to VirtualBox
2. Start VirtualBox and add the Windows XP VM
3. Create a host network
4. Close VirtualBox

Or Headless:
```bash
sudo VBoxManage hostonlyif create
VBoxManage registervm ~/cuckoo_sandbox/windows_xp_cuckoo_vm/windows_xp_cuckoo_vm.vbox
```

##### Configure Cuckoo

Edit ~/cuckoo_sandbox/cuckoo/conf/cuckoo.conf with the following changes:
```
# Under the [timeouts] section set the default timeout
default = 10
```

Edit ~/cuckoo_sandbox/cuckoo/conf/virtualbox.conf with the following changes:
```
# Under the [virtualbox] section
mode = headless
# Under the [cuckoo1] section
label = windows_xp_cuckoo_vm
# Our Windows XP VM has a snapshot named Snapshot1
snapshot = Snapshot1
```

#### Launching ODA

Make sure apache2 is running
```bash
sudo /etc/init.d/apache2 restart
```

In another terminal, run NodeJS
```bash
cd $ODA_SRC_DIR/nodejs
node socket_app.js
```

In another terminal, start the main Cuckoo server:
```bash
cd ~/cuckoo_sandbox/cuckoo
sudo ./cuckoo -d
```

In another terminal, start the Cuckoo API server in another terminal:
```bash
cd ~/cuckoo_sandbox/cuckoo
sudo ./utils/api.py
```
