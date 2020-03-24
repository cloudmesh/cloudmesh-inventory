from __future__ import print_function

from pprint import pprint

from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.host.host import Host
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.common.util import path_expand
from cloudmesh.shell.command import map_parameters
import os
from cloudmesh.common.Shell import Shell
import sys
from cloudmesh.common.console import Console

class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION [--dryrun]
              host ssh NAMES COMMAND [--dryrun]
              host key create NAMES [--user=USER] [--dryrun]
              host key list NAMES
              host key update FILE [--dryrun]
              host key scp NAMES FILE [--dryrun]
              host key gather NAMES [FILE]
              host key scatter NAMES [FILE]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --dryrun   shows what would be done but does not execute

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
                       'user')
        dryrun = arguments.dryrun

        if dryrun:
            VERBOSE(arguments)

        if arguments.scp and not arguments.key:

            destinations = Parameter.expand(arguments.DESTINATION)
            source = arguments.SOURCE
            results = Host.scp(source, destinations, output="lines")

        elif arguments.ssh:
            names = Parameter.expand(arguments.NAMES)

            # print (names)

            results = Host.ssh(hosts=names, command=arguments.COMMAND)
            print (arguments.COMMAND)
            pprint(results)

        elif arguments.key and arguments.create:

            names = Parameter.expand(arguments.NAMES)
            command = 'ssh-keygen -q -N "" -f ~/.ssh/id_rsa <<< y'
            results = Host.ssh(hosts=names,
                               command=command,
                               username=arguments.user,
                               dryrun=dryrun,
                               executor=os.system)
            results = Host.ssh(hosts=names,
                               command='cat .ssh/id_rsa.pub',
                               username=arguments.user)

            pprint(results)


        elif arguments.key and arguments.list:

            names = Parameter.expand(arguments.NAMES)

            results = Host.ssh(hosts=names,
                               command='cat .ssh/id_rsa.pub',
                               username=arguments.user)

            pprint(results)



        elif arguments.key and arguments.gather:

            VERBOSE(arguments)

            names = Parameter.expand(arguments.NAMES)

            results = Host.ssh(hosts=names,
                               command='cat .ssh/id_rsa.pub',
                               username=arguments.user,
                               verbose=False)

            if results is None:
                Console.error("No keys found")
                return ""


            output = "\n".join(element["stdout"] for element in results)

            if arguments.FILE:
                filename = path_expand(arguments.FILE)
                print ("FFF", filename)

                directory = os.path.dirname(filename)
                if directory:
                    print ("D", directory)
                    Shell.mkdir(directory)
                with open (filename, "w") as f:
                    f.write(output)
            else:
                print(output)

        elif arguments.key and arguments.scatter:

            names = Parameter.expand(arguments.NAMES)
            file = arguments.get("FILE") or \
                   path_expand("~/.cloudmesh/keys/authorized_keys")
            Host.scatter(names, file, "~/.ssh/authorized_keys")



        elif arguments.key and arguments.update:
            raise NotImplementedError

            """
            Host.fix_keys_file(arguments.FILE)
            """

        elif arguments.key and arguments.scp:

            raise NotImplementedError

            """
            Host.fix_keys_file(arguments.FILE)
            names = Parameter.expand(arguments.NAMES)

            for name in names:
                destinations = [f"{name}:~/.ssh/authorized_keys"]
                results = Host.scp(arguments.FILE, destinations, dryrun=dryrun)
            """

        return ""
