from pprint import pprint

from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.inventory.inventory import Inventory
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command, map_parameters


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
              inventory create TAG [--manager=MANAGER]
                                          [--workers=WORKERS]
                                          [--ip=IP]
                                          [--inventory=INVENTORY]
                                          [--keyfile=KEYFILE]
              inventory set NAMES ATTRIBUTE to VALUES [--inventory=INVENTORY]
              [--listvalue]
              inventory delete NAMES [--inventory=INVENTORY]
              inventory clone NAMES from SOURCE [--inventory=INVENTORY]
              inventory list [NAMES] [--format=FORMAT] [--columns=COLUMNS] [--inventory=INVENTORY]
              inventory info [--inventory=INVENTORY]

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
                       'manager',
                       'workers',
                       'ip',
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

        elif arguments.NAMES is not None and arguments.list:

            hosts = Parameter.expand(arguments.NAMES)

            print(hosts)
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

            manager = arguments.manager
            workers = arguments.workers
            ips = arguments.ip
            inventory = arguments.inventory
            keyfile = arguments.keyfile or '~/.ssh/id_rsa.pub'

            if ips is None or ',' not in ips:
                Console.error(
                    "Missing comma delimiter between master IP and worker IPs in --ip")
                return
            if manager is None:
                Console.error("Missing --manager param")
                return
            if workers is None:
                Console.error("Missing --workers param")
                return
            if inventory is None:
                Console.error("Missing --inventory param")
                return

            manager_ip, worker_ips = ips.split(',')
            worker_ips = Parameter.expand(worker_ips)
            worker_hostnames = Parameter.expand(workers)

            if len(worker_ips) != len(worker_hostnames):
                Console.error(
                    "Length of worker IPs does not match length of worker hostnames")
                return

            if arguments.inventory is None:
                i = Inventory()
            else:
                i = Inventory(f'~/.cloudmesh/{arguments.inventory}')
            i.read()

            i.add(host=manager,
                  name=manager,
                  tag=tag,
                  cluster=inventory.split('.')[0],
                  service='manager',
                  ip=manager_ip,
                  keyfile=keyfile,
                  status="inactive"
                  )

            for worker_hostname, worker_ip in zip(worker_hostnames, worker_ips):
                i.add(host=worker_hostname,
                      name=worker_hostname,
                      tag=tag,
                      cluster=inventory.split('.')[0],
                      service='worker',
                      ip=worker_ip,
                      keyfile=keyfile,
                      status="inactive"
                )  # noqa: E124

            i.save()
            Console.ok(f"Successfuly saved to ~/.cloudmesh/{inventory}")

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
