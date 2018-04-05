from __future__ import print_function
from future.utils import iteritems
from cloudmesh.common.Shell import Shell
from cloudmesh.common.ConfigDict import ConfigDict
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import banner
from cloudmesh.common.locations import config_file
from cloudmesh.common.locations import config_dir_setup
from cloudmesh.common.console import Console
from cloudmesh.common.Printer import Printer
from pprint import pprint
import json
import yaml
import hostlist
import sys
import os.path


class Inventory(object):
    def info(self):
        self.filename = path_expand("~/.cloudmesh/inventory.yaml")

        banner("Configuration")
        Console.ok('Data File: {:}'.format(self.filename))
        Console.ok('Object Attributes: {:}'.format(', '.join(self.order)))
        Console.ok('Objects: {:}'.format(len(self.data)))
        print(70 * "#")

    def __init__(self):

        self.order = [
            "host",
            "name",
            "cluster",
            "label",
            "service",
            "ip",
            "project",
            "owners",
            "comment"]

        self.entry = {}
        for key in self.order:
            self.entry[key] = ""

        self.data = {}

        self.filename = path_expand("~/.cloudmesh/inventory.yaml")
        self.read(self.filename)

    def read(self, filename=None):
        if filename is not None:
            self.filename = filename

        # if not os.path.isfile(filename):
        #    self.save(filename)
        stream = open(self.filename, "r")
        self.data = yaml.safe_load(stream)
        stream.close()

    def save(self, filename=None, format="yaml"):
        if filename is None:
            filename = self.filename
        with open(filename, 'w') as yaml_file:
            yaml_file.write(self.list(format=format))

    def add(self, **kwargs):

        if "host" not in kwargs:
            print("ERROR no id specified")
            sys.exit(1)

        hosts = hostlist.expand_hostlist(kwargs['host'])

        for host in hosts:
            if host in self.data:
                entry = self.data[host]
            else:
                entry = dict(self.entry)
                self.data[host] = entry
            for key, value in kwargs.iteritems():
                entry[key] = value
            entry['host'] = host
            for attribute in entry:
                self.data[host][attribute] = entry[attribute]
        self.save()

    def list(self, format='dict', sort_keys=True, order=None):
        if order is None:
            order = self.order
        header = order
        return Printer.dict(self.data,
                            header=header,
                            order=order,
                            output=format,
                            sort_keys=sort_keys)

    def _str(self, data, with_empty=False):
        print()
        for key in data:
            if self.data[key] is '' or self.data[key] is None:
                pass
            else:
                print(self.data[key])


class CommandSystem(object):
    @classmethod
    def status(cls, host):
        msg = "Unknown host"
        try:
            msg = Shell.ping("-c", "1", host)
        except:
            pass
        if "1 packets transmitted, 1 packets received" in msg:
            return True
        elif "Unknown host" in msg:
            return False
        else:
            return False


if __name__ == "__main__":
    i = Inventory()
    banner("Info")
    i.info()

    for output in ['dict', 'yaml', 'csv', 'table']:
        banner(output)
        print(i.list(format=output))

    banner("changing values")
    i.add(host="i1", cluster="india", label="india")
    i.add(host="i2", cluster="india", label="gregor")
    i.add(host="d[1-4]", cluster="delta", label="delta")

    banner("saving")
    i.save()

    for output in ['dict', 'yaml', 'csv', 'table']:
        banner(output)
        print(i.list(format=output))

    banner("reading")
    n = Inventory()
    n.read()
    print(n.list('table'))
