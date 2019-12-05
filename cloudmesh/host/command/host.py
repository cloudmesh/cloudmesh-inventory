from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.host.host import Host

class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION
              host ssh NAMES COMMAND
              host key cat NAMES
              host key fix FILE
              host key cp NAMES FILE


          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

          Description:

              host scp NAMES SOURCE DESTINATION


              host ssh NAMES COMMAND

                runs the command on all specified hosts
                Example:
                     ssh red[01-10] \"uname -a\"

              host key cat NAMES

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

              host key cp NAMES

                not implemented yet
                copies all keys the file FILE to authorized_keys on all hosts
                but also makes sure the the users ~/.ssh/id_rsa.pub key is in
                the file.


        """

        VERBOSE(arguments)

        if arguments.scp:

            destinations = Parameter.expand(arguments.DESTINATION)
            source = arguments.SOURCE
            results = Host.scp(source, destinations, output="lines")

        elif arguments.ssh:
            names = Parameter.expand(arguments.NAMES)
            results = Host.ssh(names, arguments.COMMAND)
            pprint (results)

        elif arguments.key and arguments.cat:

            names = Parameter.expand(arguments.NAMES)

            command = "cat ~/.ssh/id_rsa.pub"

            results = Host.ssh(names, command)
            pprint(results)

            result = Host.concatenate_keys(results)

            print(result)

        elif arguments.key and arguments.add:
            raise NotImplementedError

        elif arguments.key and arguments.list:

            raise NotImplementedError


        return ""
