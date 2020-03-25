from __future__ import print_function

from pprint import pprint

from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Host import Host
# from cloudmesh.host.host import Host
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import map_parameters
import os
from cloudmesh.common.Shell import Shell
import sys
from cloudmesh.common.console import Console
from cloudmesh.common.Printer import Printer


class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION [--dryrun]
              host ssh NAMES COMMAND [--dryrun] [--output=FORMAT]
              host key create NAMES [--user=USER] [--dryrun] [--output=FORMAT]
              host key list NAMES
              host key gather NAMES [--authorized_keys] [FILE]
              host key scatter NAMES FILE

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --dryrun   shows what would be done but does not execute
              --output=FORMAT  the format of the output [default: table]

          Description:

              host scp NAMES SOURCE DESTINATION


              host ssh NAMES COMMAND

                runs the command on all specified hosts
                Example:
                     ssh red[01-10] \"uname -a\"

              host key create NAMES
                create a ~/.ssh/id_rsa and id_rsa.pub on all hosts specified
                Example:
                    ssh key create red[01-10]

              host key list NAMES

                cats all id_rsa.pub keys from all hosts specifed
                 Example:
                     ssh key list red[01-10]

              host key fix FILE

                copies all keys from file FILE to authorized_keys on all hosts,
                but also makes sure that the users ~/.ssh/id_rsa.pub key is in
                the file.

                1) adds ~/.id_rsa.pub to the FILE only if its not already in it
                2) removes all duplicated keys

                Example:
                    ssh key list red[01-10] > pubkeys.txt
                    ssh key fix pubkeys.txt

              host key scp NAMES FILE

                copies all keys from file FILE to authorized_keys on all hosts
                but also makes sure that the users ~/.ssh/id_rsa.pub key is in
                the file and removes duplicates, e.g. it calls fix before upload

                Example:
                    ssh key list red[01-10] > pubkeys.txt
                    ssh key scp red[01-10] pubkeys.txt

        """
        map_parameters(arguments,
                       'dryrun',
                       'output',
                       'user')
        dryrun = arguments.dryrun

        if dryrun:
            VERBOSE(arguments)

        if arguments.scp and not arguments.key:

            destinations = Parameter.expand(arguments.DESTINATION)
            source = arguments.SOURCE
            results_key = Host.scp(source, destinations, output="lines")

        elif arguments.ssh:
            names = Parameter.expand(arguments.NAMES)

            # print (names)

            results = Host.ssh(hosts=names,
                               command=arguments.COMMAND)

            if arguments.output == 'table':
                print(Printer.write(results,
                                    order=['host', 'success', 'stdout']))
            else:
                pprint(results)

        elif arguments.key and arguments.create:

            results = Host.ssh_keygen(
                hosts=arguments.NAMES,
                username=arguments.user,
                dryrun=dryrun)

            if arguments.output == 'table':
                print(Printer.write(results,
                                    order=['host', 'success', 'stdout']))
            else:
                pprint(results)


        elif arguments.key and arguments.list:

            names = Parameter.expand(arguments.NAMES)

            results_key = Host.ssh(hosts=names,
                                   command='cat .ssh/id_rsa.pub',
                                   username=arguments.user)

            pprint(results_key)



        elif arguments.key and arguments.gather:

            VERBOSE(arguments)

            names = Parameter.expand(arguments.NAMES)

            results_key = Host.ssh(hosts=names,
                                   command='cat .ssh/id_rsa.pub',
                                   username=arguments.user,
                                   verbose=False)
            results_authorized = Host.ssh(hosts=names,
                                          command='cat .ssh/authorized_keys',
                                          username=arguments.user,
                                          verbose=False)

            # remove duplicates

            if results_key is None and results_authorized is None:
                Console.error("No keys found")
                return ""

            # geting the output and also removing duplicates
            output = list(set(
                [element["stdout"] for element in results_key] +
                [element["stdout"] for element in results_authorized]
            ))

            output = '\n'.join(output)

            if arguments.FILE:
                filename = path_expand(arguments.FILE)
                directory = os.path.dirname(filename)
                if directory:
                    Shell.mkdir(directory)
                with open(filename, "w") as f:
                    f.write(output)
            else:
                print(output)


        elif arguments.key and arguments.scatter:

            names = arguments.NAMES
            file = arguments.get("FILE")

            if not os.path.isfile(file):
                Console.error("The file does not exist")
                return ""

            # Host.scatter(hosts=names, source=file, destination=".ssh/authorized_keys")

            from cloudmesh.common.Host import Host as ParallelHost

            result = ParallelHost.run(
                hosts=names,
                command='ssh {host} uname',
                shell=True)
            pprint(result)

        return ""
