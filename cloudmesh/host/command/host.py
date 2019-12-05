from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.host.api.manager import Manager
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
              host key add NAMES
              host key list NAMES
              host key distribute NAMES


          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              -f      specify the file

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
