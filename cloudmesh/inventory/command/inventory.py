from pprint import pprint
import os

from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.inventory.inventory import Inventory
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters
from cloudmesh.common.Host import Host
from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand

class InventoryCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_inventory(self, args, arguments):
        """
        ::

          Usage:
              inventory add NAMES [--label=LABEL]
                                  [--services=SERVICES]
                                  [--project=PROJECT]
                                  [--owners=OWNERS]
                                  [--comment=COMMENT]
                                  [--inventory=INVENTORY]
                                  [--cluster=CLUSTER]
                                  [--ip=IP]
                                  [--service=SERVICE]
                                  [--tag=TAG]
                                  [--keyfile=KEYFILE]
              inventory create TAG [--hostnames=NAMES]
                                   [--ip=IP]
                                   [--inventory=INVENTORY]
                                   [--keyfile=KEYFILE]
              inventory set NAMES ATTRIBUTE to VALUES [--inventory=INVENTORY] [--listvalue]
              inventory delete NAMES [--inventory=INVENTORY]
              inventory clone NAMES from SOURCE [--inventory=INVENTORY]
              inventory list [NAMES] [--format=FORMAT] [--columns=COLUMNS] [--inventory=INVENTORY]
              inventory info [--inventory=INVENTORY]
              inventory remove --inventory=INVENTORY

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
             --keyfile=KEYFILE      Keyfile to assign [default: ~/.ssh/id_rsa.pub]

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

            cms inventory list
                lists the repository

            cms inventory set x[3-4] temperature to 32
                sets for the resources x3, x4 the value of the
                temperature to 32

            cms inventory set x[7-8] ip to 128.0.0.[0-1]
                sets the value of x7 to 128.0.0.0
                sets the value of x8 to 128.0.0.1

            cms inventory set x1 services to bridge,kubernetes --listvalue
                sets the value of x1 to [bridge, kubernetes]
                The --listvalue option indicates the value set is a list

            cms inventory clone x[5-6] from x3
                clones the values for x5, x6 from x3

        """
        map_parameters(arguments,
                       "columns",
                       'ip',
                       'hostnames',
                       'inventory',
                       'keyfile',
                       'listvalue')

        if arguments.info:

            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()
            i.info()

        elif arguments.remove and arguments.inventory:

            os.system("rm -f " + path_expand(f'~/.cloudmesh/{arguments.inventory}'))

        elif arguments.NAMES is not None and arguments.list:

            hosts = Parameter.expand(arguments.NAMES)

            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()
            d = dict(i.data)
            r = {}
            for key in d:
                if key in hosts:
                    r[key] = d[key]

            pprint(r)
            i.data = r

            if arguments["--columns"]:
                order = arguments["--columns"].split(",")
            else:
                order = i.order
            print(i.list(format="table", order=order))

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

        elif arguments.create:
            tag = arguments.TAG

            hostnames = Parameter.expand(arguments.hostnames)
            manager, workers = Host.get_hostnames(hostnames)

            ips = Parameter.expand(arguments.ip)

            if len(ips) != len(hostnames):
                Console.error("The number of hosts does not match the number of ips")
                return

            keyfile = arguments.keyfile or '~/.ssh/id_rsa.pub'

            if arguments.inventory is None:
                Console.error("Missing --inventory param")
                return

            if manager is None:
                manager_ip = None
                worker_ips = ips
            else:
                manager_ip = ips[0]
                worker_ips = ips[1:]

            worker_hostnames = workers


            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()

            inventory_name = arguments.inventory.split('.')[0]

            i.add(host=manager,
                  name=manager,
                  tag=tag,
                  cluster=inventory_name,
                  service='manager',
                  ip=manager_ip,
                  keyfile=keyfile,
                  status="inactive"
                  )

            for worker, ip in zip(worker_hostnames, worker_ips):
                i.add(host=worker,
                      name=worker,
                      tag=tag,
                      cluster=inventory_name,
                      service='worker',
                      ip=ip,
                      keyfile=keyfile,
                      status="inactive"
                )  # noqa: E124

            i.save()
            Console.ok(f"Successfuly saved to ~/.cloudmesh/{arguments.inventory}")

        elif arguments.list:

            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()
            if arguments["--columns"]:
                order = arguments["--columns"].split(",")
            else:
                order = i.order
            print(i.list(format="table", order=order))

        elif arguments.set:

            hosts = Parameter.expand(arguments.NAMES)
            values = Parameter.expand(arguments.VALUES)
            if len(values) == 1:
                values = values * len(hosts)
            attribute = arguments.ATTRIBUTE
            if not arguments.listvalue and len(hosts) != len(values):
                Console.error(
                    "Number of names {:} != number of values{:}".format(
                        len(hosts), len(values)))
            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()

            for index in range(0, len(hosts)):
                host = hosts[index]
                value = values if arguments.listvalue else values[index]

                if not i.has_host(host):
                    i.add(host=host)

                i.set(host, attribute, value)
                # object = {'host': host,
                #           attribute: value}

                # i.add(**object)
                i.save()

            print(i.list(format="table"))

        elif arguments.add:

            hosts = Parameter.expand(arguments.NAMES)
            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()
            element = {}

            for attribute in i.order:
                try:
                    value = arguments["--" + attribute]
                    if value is not None:
                        element[attribute] = value
                except Exception as e:  # noqa: F841
                    pass
            element['host'] = arguments.NAMES
            element['status'] = 'inactive'
            element['name'] = arguments.NAMES
            i.add(**element)
            i.save()
            print(i.list(format="table"))

        elif arguments.delete:

            hosts = Parameter.expand(arguments.NAMES)
            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()

            for host in hosts:
                i.delete(host)
            i.save()

        elif arguments.clone:

            hosts = Parameter.expand(arguments.NAMES)
            source = arguments.SOURCE

            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()

            if source in i.data:

                for host in hosts:
                    i.data[host] = dict(i.data[source])
                i.save()
            else:
                Console.error("The source {:} does not exist".format(source))

        return ""
