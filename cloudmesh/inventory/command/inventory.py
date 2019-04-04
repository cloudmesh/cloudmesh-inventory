from __future__ import print_function
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.shell.command import PluginCommand
from cloudmesh.inventory.api.data import Inventory
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.parameter import Parameter
from cloudmeh.management.configuration.config import Config
class InventoryCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_inventory(self, args, arguments):
        """
        ::

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

            cm lists

                lists the repository

            cm x[3-4] set temperature to 32

                sets for the resources x3, x4 the value of the
                temperature to 32

            cm x[7-8] set ip 128.0.0.[0-1]

                sets the value of x7 to 128.0.0.0
                sets the value of x8 to 128.0.0.1

            cm clone x[5-6] from x3

                clones the values for x5, x6 from x3

        """
        map_parameters(arguments,
                       "columns")
        print(arguments)
        #
        # TODO: fix config reader, suse cmd4
        #
        filename = Config(config_path="/cloudmesh_inventory.yaml")

        sorted_keys = True
        if arguments.info:

            i = Inventory()
            i.read()
            i.info()

        elif arguments.list:

            i = Inventory()
            i.read()
            if arguments["--columns"]:
                order = arguments["--columns"].split(",")
            else:
                order = i.order
            print(i.list(format="table", order=order))

        elif arguments.NAMES is None:

            Console.error("Please specify a host name")
        # elif arguments["set"]:
        #    hosts = hostlist.expand_hostlist(arguments.NAMES)
        #    i = inventory()
        #    i.read()
        #    element = {}

        #    for attribute in i.order:
        #        try:
        #            attribute = arguments["ATTRIBUTE"]
        #            value = arguments["VALUE"]
        #            if value is not None:
        #                element[attribute] = value
        #        except:
        #            pass
        #    element['host'] = arguments.NAMES
        #    i.add(**element)
        #    print (i.list(format="table"))

        elif arguments.set:

            hosts = Parameter.expand(arguments.NAMES)
            values = Parameter.expand(arguments.VALUES)
            if len(values) == 1:
                values = values * len(hosts)
            print(hosts)
            print(values)
            attribute = arguments.ATTRIBUTE
            if len(hosts) != len(values):
                Console.error(
                    "Number of names {:} != number of values{:}".format(
                        len(hosts), len(values)))

            i = Inventory()
            i.read()

            for index in range(0, len(hosts)):
                host = hosts[index]
                value = values[index]

                object = {'host': host,
                          attribute: value}

                i.add(**object)

            print(i.list(format="table"))

        elif arguments.add:

            hosts = Parameter.expand(arguments.NAMES)
            i = Inventory()
            i.read()
            element = {}

            for attribute in i.order:
                try:
                    value = arguments["--" + attribute]
                    if value is not None:
                        element[attribute] = value
                except:
                    pass
            element['host'] = arguments.NAMES
            i.add(**element)
            print(i.list(format="table"))

        elif arguments.delete:

            hosts = Parameter.expand(arguments.NAMES)
            i = Inventory()
            i.read()

            for host in hosts:
                del i.data[host]
            i.save()

        elif arguments.clone:

            hosts = Parameter.expand(arguments.NAMES)
            source = arguments.SOURCE

            i = Inventory()
            i.read()

            if source in i.data:

                for host in hosts:
                    i.data[host] = dict(i.data[source])
                i.save()
            else:
                Console.error("The source {:} does not exist".format(source))

        return ""