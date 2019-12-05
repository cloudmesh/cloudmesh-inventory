from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.host.host import Host
from cloudmesh.common.util import readfile, writefile

class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION [--dryrun]
              host ssh NAMES COMMAND [--dryrun]
              host key list NAMES [--dryrun]
              host key fix FILE [--dryrun]
              host key scp NAMES FILE [--dryrun]


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

              host key list NAMES

                cats all id_rsa.pub keys from all hosts specifed
                 Example:
                     ssh key red[01-10] cat

              host key fix FILE

                not implemented yet

                copies all keys the file FILE to authorized_keys on all hosts
                but also makes sure the the users ~/.ssh/id_rsa.pub key is in
                the file.

                1) adds ~/.id_ras.pub to the FILE only if its not already in it
                2) removes all duplicated keys

              host key scp NAMES FILE

                not implemented yet

                copies all keys the file FILE to authorized_keys on all hosts
                but also makes sure the the users ~/.ssh/id_rsa.pub key is in
                the file, e.g. it calls fix before upload

        """
        dryrun = arguments["--dryrun"]

        if dryrun:
            VERBOSE(arguments)

        if arguments.scp and not arguments.key:

            destinations = Parameter.expand(arguments.DESTINATION)
            source = arguments.SOURCE
            results = Host.scp(source, destinations, output="lines")

        elif arguments.ssh:
            names = Parameter.expand(arguments.NAMES)
            results = Host.ssh(names, arguments.COMMAND)
            pprint (results)

        elif arguments.key and arguments.list:

            names = Parameter.expand(arguments.NAMES)

            command = "cat ~/.ssh/id_rsa.pub"

            results = Host.ssh(names, command, dryrun=dryrun)
            # pprint(results)

            result = Host.concatenate_keys(results)

            if not dryrun:
                print(result)

        elif arguments.key and arguments.fix:

            #
            # concatenate ~/.ssh/id_rsa.pub
            #
            lines = readfile(arguments.FILE)
            key = readfile(path_expand("~/.ssh/id_rsa.pub"))

            authorized_keys = lines + key

            #
            # remove duplicated lines
            #

            keys = ''.join(authorized_keys)
            keys = '\n'.join(list(set(keys.splitlines())))


            writefile(arguments.FILE, str(keys))


        elif arguments.key and arguments.scp:

            source = path_expand("~/.ssh/authorized_keys")

            names = Parameter.expand(arguments.NAMES)

            for name in names:
                destinations = [f"{name}:~/.ssh/authorized_keys"]
                results = Host.scp(source, destinations, dryrun=dryrun)

        print()

        return ""
