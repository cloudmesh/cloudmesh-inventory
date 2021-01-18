# Cloudmesh Inventory

[![Version](https://img.shields.io/pypi/v/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/cloudmesh-inventory/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Format](https://img.shields.io/pypi/format/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Format](https://img.shields.io/pypi/status/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Travis](https://travis-ci.com/cloudmesh/cloudmesh-inventory.svg?branch=main)](https://travis-ci.com/cloudmesh/cloudmesh-inventory)


<!--TOC-->

- [Cloudmesh Inventory](#cloudmesh-inventory)
  - [Introduction](#introduction)
  - [Cloudmesh Manual](#cloudmesh-manual)
  - [Instalation and Documentation](#instalation-and-documentation)
    - [Instalation with pip](#instalation-with-pip)
    - [Instalation from source](#instalation-from-source)
    - [Configuration](#configuration)
  - [BUGS](#bugs)
  - [Manpage](#manpage)

<!--TOC-->

## Introduction

Often we need a convenient way to manage inventories for Computers and Services. One whay to do this is in databases or flat files, or dedicated services. Cloudmesh Inventory is designed to be at this time super simple and provides a list of computer entries that are used to document if a service is running on it. It uses a very small set of metadata to keep it extremely simple. All attribute values are strings. An example is 

    g001:
      cluster: gregor
      comment: test
      host: g001
      ip: 127.0.0.1
      label: g001
      metadata: None
      name: g001
      owners: gvonlasz
      project: cloudmesh
      service: compute

We explain our intended use of the attributes next 

| Attribute | Description |
| --- | ---| 
| cluster | The name of the cluster this entry is associated with | 
| description | a description | 
| comment | a comment | 
| host | the unique name of the host | 
| ip | the ip address |
| name | a unique hostname for the entry |
| label | a unique label that may include more than the hostname |
| metadata | a string in which metadata can be placed |
| owners | a list of owners of the machine (comma separated) |
| project | a string representiing a project name |
| service | a string representing the service |
| os | name of the operating system |


## Cloudmesh Manual

The manual for cloudmesh can be found at 

* https://cloudmesh.github.io/cloudmesh-manual/

Cloudmesh Inventory, however can also be used as standalone product.

## Instalation and Documentation

Make sure you have a new version of python and pip. We tested with with versions greater then

* python 3.7.3
* pip 19.0.3

### Instalation with pip

You will need the followng other cloudmesh modules before you can
install via pip:

```bash
$ pip insatll cloudmesh-common
$ pip insatll cloudmesh-cmd5
$ pip insatll cloudmesh-inventory
```

### Instalation from source

As developer we recommend yo use the instalation from source. For this we have a convenient cloudmesh installer program that outomates fetching the source and does the install for you.
To install it form source use:


    $ mkdir ~/cm
    $ cd ~/cm
    
    $ pip install cloudmesh-installer    
    $ cloudmesh-installer git clone inventory
    $ cloudmesh-installer install inventory
    
This will clone a number of repositories in the `cm` directory and
install them with  `pip` from them.

### Configuration

Your inventory will be located at

    ~/.cloudmesh/inventory.yaml

An example file will look as follows:

    g001:
      cluster: gregor
      comment: test
      host: g001
      ip: 127.0.0.1
      label: g001
      metadata: None
      name: g001
      owners: gvonlasz
      project: cloudmesh
      service: compute
      os: ubuntu20.04
    g002:
      cluster: gregor
      comment: test
      host: g002
      ip: 127.0.0.1
      label: g002
      metadata: None
      name: g002
      owners: gvonlasz
      project: cloudmesh
      service: compute
      os: ubuntu20.04

## BUGS

If you like to see fetures added or find bugs, please let us know.

## Manpage

<!--MANUAL-->
```
    inventory add NAMES [--label=LABEL]
                        [--service=SERVICES]
                        [--project=PROJECT]
                        [--owners=OWNERS]
                        [--comment=COMMENT]
                        [--cluster=CLUSTER]
                        [--ip=IP]
    inventory set NAMES ATTRIBUTE to VALUES
    inventory delete NAMES
    inventory clone NAMES from SOURCE
    inventory list [NAMES] [--format=FORMAT] [--columns=COLUMNS]
    inventory info

Arguments:
  NAMES     Name of the resources (example i[10-20])
  FORMAT    The format of the output is either txt,
            yaml, dict, table [default: table].
  OWNERS    a comma separated list of owners for this resource
  LABEL     a unique label for this resource
  SERVICE   a string that identifies the service
  PROJECT   a string that identifies the project
  SOURCE    a single host name to clone from
  COMMENT   a comment

Options:
   -v       verbose mode

Description:

      add -- adds a resource to the resource inventory
      list -- lists the resources in the given format
      delete -- deletes objects from the table
      clone -- copies the content of an existing object
               and creates new once with it
      set   -- sets for the specified objects the attribute
               to the given value or values. If multiple values
               are used the values are assigned to the and
               objects in order. See examples
      map   -- allows to set attributes on a set of objects
               with a set of values

Examples:

  cms inventory add x[0-3] --service=openstack
      adds hosts x0, x1, x2, x3 and puts the string
      openstack into the service column

  cms inventory lists
      lists the repository

  cms inventory x[3-4] set temperature to 32
      sets for the resources x3, x4 the value of the
      temperature to 32

  cms inventory x[7-8] set ip 128.0.0.[0-1]
      sets the value of x7 to 128.0.0.0
      sets the value of x8 to 128.0.0.1

  cms inventory clone x[5-6] from x3
      clones the values for x5, x6 from x3

```
<!--MANUAL-->

