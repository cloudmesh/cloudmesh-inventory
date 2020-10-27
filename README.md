# Cloudmesh Inventory

[![Version](https://img.shields.io/pypi/v/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/cloudmesh/cloudmesh-inventory/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Format](https://img.shields.io/pypi/format/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Format](https://img.shields.io/pypi/status/cloudmesh-inventory.svg)](https://pypi.python.org/pypi/cloudmesh-inventory)
[![Travis](https://travis-ci.com/cloudmesh/cloudmesh-inventory.svg?branch=main)](https://travis-ci.com/cloudmesh/cloudmesh-inventory)


## Instalation and Documentation

Please note that several packages are available which are pointed to in the
instalation documentation.

|  | Links |
|---------------|-------|
| Documentation | <https://cloudmesh.github.io/cloudmesh-cloud> |
| Code | <https://github.com/cloudmesh/cloudmesh-inventory> |
| Instalation Instructions | <https://github.com/cloudmesh/get> |

Sometimes its necessary to maintain a simple inventory. Naturally if you
know python you can do this with dicts. However to manage a large number
of items with repeated values its is of advantage to do this from the
commandline.

We have written such a tool that lets you easily manage the resources in
a table format.

## Installation

Make sure you have a new version of python and pip. We tested with

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

To install it form source (which is the current method) use:


    $ mkdir ~/cm
    $ cd ~/cm
    
    $ pip install cloudmesh-installer    
    $ cloudmesh-installer git clone inventory
    $ cloudmesh-installer install inventory
    
This will clone a number of repositories in the `cm` directory and
install them with   `pip` from them.

Configuration
-------------

Your inventory will be located at

    ~/.cloudmesh/inventory.yaml

You can also change the yaml file by hand, but the cm command is more
convenient.

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

BUGS
----

If you like to see fetures added or find bugs, please let us know.

Manpage
-------

    Usage:
        inventory add NAMES [--label=LABEL]
                            [--service=SERVICES]
                            [--project=PROJECT]
                            [--owners=OWNERS]
                            [--comment=COMMENT]
                            [--cluster=CLUSTER]
                            [--ip=IP]
        inventory set NAMES for ATTRIBUTE to VALUES
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

          map   -- allows to set attibutes on a set of objects
                   with a set of values

    Examples:

      cm inventory add x[0-3] --service=openstack

          adds hosts x0, x1, x2, x3 and puts the string
          openstack into the service column

      cm lits

          lists the repository

      cm x[3-4] set temperature to 32

          sets for the resources x3, x4 the value of the
          temperature to 32

      cm x[7-8] set ip 128.0.0.[0-1]

          sets the value of x7 to 128.0.0.0
          sets the value of x8 to 128.0.0.1

      cm clone x[5-6] from x3

          clones the values for x5, x6 from x3
