import os.path
import shutil
import sys
from pathlib import Path

import cloudmesh.inventory.etc as etc
import hostlist
import yaml
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables


class Inventory(object):

    def info(self):
        self.filename = path_expand(self.filename)

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
            "comment",
            "description"]

        self.entry = {}
        for key in self.order:
            self.entry[key] = ""

        self.data = {}

        self.filename = path_expand("~/.cloudmesh/inventory.yaml")
        if not os.path.exists(self.filename):
            source = Path(os.path.dirname(etc.__file__) + "/inventory.yaml")
            shutil.copyfile(source, self.filename)

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
            Console.error("no id specified")
            sys.exit(1)

        hosts = hostlist.expand_hostlist(kwargs['host'])

        for host in hosts:
            if host in self.data:
                entry = self.data[host]
            else:
                entry = dict(self.entry)
                self.data[host] = entry
            for key, value in kwargs.items():
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
            if self.data[key] == '' or self.data[key] is None:
                pass
            else:
                print(self.data[key])

class ClusterInventory(Inventory):

    def __init__(self, filename=None):

        if filename is None:
            variables = Variables()
            self.filename = variables["inventory"] or \
                            path_expand("~/.cloudmesh/inventory/cluster/cluster.yaml")

        else:
            self.filename = path_expand(filename)

        #Gregors proposal
        #    "host",        # red
        #    "name",        # red
        #    "cluster",     # cluster
        #    "label",       # manager
        #    "service",     # <- manager or worker
        #    "services",    # ["kubernetes"]
        #    "ip",          # 10.0.0.1
        #    "project",     # picluster
        #    "owners",      # ['gregor', 'richard']
        #    "comment",     # The manager node
        #    "description", # The manager for gregors cluster
        #    "keyfile",     # ~/.cloudmesh/inventory/cluster/authorized_keys_master
        #    "status"       # inidcates the status: active, inactive, ...

        # self.order = [
        #        "host",
        #        "name",
        #        "cluster",
        #        "label",
        #        "service",
        #        "services",
        #        "ip",
        #        "project",
        #        "owners",
        #        # "comment",
        #        # "description",
        #        "keyfile",
        #        "status"
        # ]
        # self.header = [
        #        "Host",
        #        "Name",
        #        "Cluster",
        #        "Label",
        #        "Service",
        #        "Services",
        #        "IP",
        #        "Project",
        #        "Owners",
        #        # "Comment",
        #        # "Description",
        #        "Keyfile",
        #        "Status"
        # ]

        self.order = [
            "name",
            "type",
            "tag",
            "manager",
            "managerIP",
            "workers",
            "keyfile"
        ]
        self.entry = {}
        self.data = {}

        for key in self.order:
            if key == "workers" or key == "manager":
                self.data[key] = {}
            else:
                self.data[key] = ""

        if not os.path.exists(self.filename):
            Path(self.filename).touch()
            self.save()

        self.read(self.filename)

    def workers(self):
        """
        Returns the list of workers

        :return: list of workers
        :rtype: dict
        """
        return self.find(service="worker")

    def manager(self):
        """
        Returns the list managers

        :return: list of menagers. If only one manager it returns an item not a list
        :rtype: list or single item
        """
        manager = self.find(service="manager")
        if len(maneger) == 1:
            return manager[0]
        else:
            return manager

    def find(self, **kwargs):
        """
        return the list of items eapal to the arguments set

        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        # THIS IS NOT TESTED, JUST DRAFTED
        # this is wrong as it assumes not a dict but a list
        found = []
        for entry in self.data:
            match = True
            for t in kwargs:
                match = match and kwargs[t] == data[t]
            if match:
                found.append(entry)
        return found

    def set(self, name=None, attribute=None, value=None):
        """
        sets for the named element the attribute to the value
        :param name:
        :type name:
        :param value:
        :type value:
        :return:
        :rtype:
        """
        raise NotImplementedError

    def get(self, name, attribute):
        """
        returns the value of the attribute of the named element

        :param name:
        :type name:
        :param attribute:
        :type attribute:
        :return:
        :rtype:
        """
        return self.data[name][attribute]

    def activate(self, name):
        """
        activates a node

        :param name:
        :type name:
        :return:
        :rtype:
        """
        self.set(name, attribute="status", value="active")

    def deactivate(self, name):
        """
        activates a node

        :param name:
        :type name:
        :return:
        :rtype:
        """
        self.set(name, attribute="status", value="inactive")

    def print(self, order=None, header=None, output="table"):
        """
        prints the inventory in the output format

        :param order:
        :type order:
        :param header:
        :type header:
        :return:
        :rtype:
        """
        order = order or self.order
        header = header or self.header
        print(Printer.write(self.data, order=order, header=header))

    def add(self, **kwargs):
        for attribute in kwargs:
            name = kwargs["name"]
            self.set(name, attribute=attribute, value=kwargs[attribute])

    def set_keyfile(self, keyfile):
        self.data["keyfile"] = keyfile

    def set_name(self, name):
        self.data["name"] = name

    def set_manager(self, manager, manager_ip):
        self.data["manager"] = manager
        self.data["managerIP"] = manager_ip

    def add_worker(self, worker, worker_ip):
        self.data["workers"][worker] = worker_ip
    
    def set_type(self, os_type):
        self.data["type"] = os_type
    
    def set_tag(self, tag):
        self.data["tag"] = tag

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
