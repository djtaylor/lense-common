# Lense Common Libraries

Common libraries shared by the Lense engine, client, and portal applications.

### Repository (Unavailable)

To make the Lense packages available, you will need to add the following PPA and import the signing key:

```sh
$ sudo add-apt-repository ppa:djtaylor13/main
$ sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DAA6AF94
$ sudo apt-get update
```

### Installation

You can install 'lense-common' and its requirements with the following commands:

```sh
$ sudo apt-get install lense-common
$ sudo pip install -r /usr/share/doc/lense/requirements.txt
```

Note that this will satisfy Python requirements for: lense-client, lense-engine, lense-portal

### Installation (All-in-One)

If you are installing of the Lense projects on one machine, you can run the following commands to get your installation up and running:

```sh
$ sudo apt-get install lense-common lense-client lense-engine lense-portal
$ sudo pip install -r /usr/share/doc/lense/requirements.txt
$ sudo lense-bootstrap
```