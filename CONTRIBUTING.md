## How to contribute

### Launching your own ODA instance

In order to simplify ODA development environment installation and configuration,
we use VirtualBox+Vagrant+Ansible to provision a consistent development machine.

#### Installing prerequisites

* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

#### Launching Vagrant

Launching Vagrant will create a new Ubuntu 16.04 VM in VirtualBox, then
provision ODA using Ansible:
```
vagrant up
```
Once Vagrant has provisioned the VM, you can login using:
```
vagrant ssh
```

#### Executing tests

Most of ODA's core code is Django.  We use the typical Django Python `unittest`
framework for testing:
```
vagrant ssh
cd site/oda
./manage.py test
```

#### Starting and accessing ODA web application

ODA's core application can be started using:
```
vagrant ssh
cd site/oda
./manage.py runserver 0.0.0.0:8000
```
The Vagrantfile exposes port `8000` on localhost, so you may access ODA using
http://localhost:8000. 

### Coding Guidelines

#### Languages
#### Style
#### Testing

### Filing an issue

#### **Did you find a bug?**

* **Ensure the bug was not already reported** b searching on GitHub under
  [Issues](https://github.com/syscall7/oda/issues).

* If you're unable to find an open issue addressing the problem, [open a new
  one](https://github.com/syscall7/oda/issues/new). Be sure to include a **title
  and clear description**, as much relevant information as possible, and a
  **code sample** or an **executable test case** demonstrating the expected
  behavior that is not occurring.

#### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.

* Ensure the PR description clearly describes the problem and solution. Include
  the relevant issue number if applicable.

#### **Did you fix whitespace, format code, or make a purely cosmetic patch?**

Changes that are cosmetic in nature and do not add anything substantial to the
stability, functionality, or testability of ODA will generally not be accepted.

#### **Do you intend to add a new feature or change an existing one?**

* Suggest your change in the TBD mailing list and start writing code.

* Do not open an issue on GitHub until you have collected positive feedback about the change. GitHub issues are primarily intended for bug reports and fixes.

#### **Do you have questions about the source code?**

* Ask any question about how to use ODA in TBD mailing list.
