import os
from pprint import pprint

from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand
# from cloudmesh.host.host import Host
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.common.util import sudo_writefile, sudo_readfile
from cloudmesh.common.util import banner

class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION [--dryrun]
              host ssh NAMES COMMAND [--dryrun] [--output=FORMAT]
              host config NAMES [IPS] [--user=USER] [--key=PUBLIC]
              host check NAMES [--user=USER] [--key=PUBLIC]
              host key create NAMES [--user=USER] [--dryrun] [--output=FORMAT]
              host key list NAMES [--output=FORMAT]
              host key gather NAMES [--authorized_keys] [FILE]
              host key scatter NAMES FILE
              host tunnel create NAMES [--port=PORT]

          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --dryrun   shows what would be done but does not execute
              --output=FORMAT  the format of the output
              --port=PORT starting local port for tunnel assignment

          Description:

              host scp NAMES SOURCE DESTINATION

                TBD

              host ssh NAMES COMMAND

                runs the command on all specified hosts
                Example:
                     ssh red[01-10] \"uname -a\"

              host key create NAMES
                create a ~/.ssh/id_rsa and id_rsa.pub on all hosts specified
                Example:
                    ssh key create "red[01-10]"

              host key list NAMES

                list all id_rsa.pub keys from all hosts specifed
                 Example:
                     ssh key list red[01-10]

              host key gather HOSTS FILE

                gathers all keys from file FILE including the one from localhost.

                    ssh key gather "red[01-10]" keys.txt

              host key scatter HOSTS FILE

                copies all keys from file FILE to authorized_keys on all hosts,
                but also makes sure that the users ~/.ssh/id_rsa.pub key is in
                the file.

                1) adds ~/.id_rsa.pub to the FILE only if its not already in it
                2) removes all duplicated keys

                Example:
                    ssh key scatter "red[01-10]"

              host key scp NAMES FILE

                copies all keys from file FILE to authorized_keys on all hosts
                but also makes sure that the users ~/.ssh/id_rsa.pub key is in
                the file and removes duplicates, e.g. it calls fix before upload

                Example:
                    ssh key list red[01-10] > pubkeys.txt
                    ssh key scp red[01-10] pubkeys.txt

              host config NAMES IPS [--user=USER] [--key=PUBLIC]

                generates an ssh config file tempalte that can be added to your
                .ssh/config file

                Example:
                    cms host config "red,red[01-03]" "198.168.1.[1-4]" --user=pi

              host check NAMES [--user=USER] [--key=PUBLIC]

                This command is used to test if you can login to the specified
                hosts. It executes the hostname command and compares it.
                It provides a table  with a sucess column

                cms host check "red,red[01-03]"

                    +-------+---------+--------+
                    | host  | success | stdout |
                    +-------+---------+--------+
                    | red   | True    | red    |
                    | red01 | True    | red01  |
                    | red02 | True    | red02  |
                    | red03 | True    | red03  |
                    +-------+---------+--------+

              host tunnel create NAMES [--port=PORT]

                This command is used to create a persistent local port
                forward on the host to permit ssh tunnelling from the wlan to
                the physical network (eth). This registers an autossh service in
                systemd with the defualt port starting at 8001.

                Example:
                    cms host tunnel create red00[1-3]
        """

        def _print(results):
            arguments.output = arguments.output or 'table'

            if arguments.output == 'table':
                print(Printer.write(results,
                                    order=['host', 'success', 'stdout']))
            else:
                pprint(results)

        map_parameters(arguments,
                       'dryrun',
                       'output',
                       'user',
                       'port')
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
            _print(results)

        elif arguments.key and arguments.create:

            results = Host.ssh_keygen(
                hosts=arguments.NAMES,
                username=arguments.user,
                dryrun=dryrun)

            _print(results)

        elif arguments.key and arguments.list:

            names = Parameter.expand(arguments.NAMES)

            results = Host.ssh(hosts=names,
                               command='cat .ssh/id_rsa.pub',
                               username=arguments.user)

            _print(results)


        elif arguments.key and arguments.gather:

            output = Host.gather_keys(
                username=arguments.user,
                hosts=arguments.NAMES,
                filename="~/.ssh/id_rsa.pub",
                key="~/.ssh/id_rsa",
                processors=3,
                dryrun=False)

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

            result = Host.put(hosts=names,
                              source=file,
                              destination=".ssh/authorized_keys")

            _print(result)

        elif arguments.config:

            key = arguments.key or "~/.ssh/id_rsa.pub"
            result = Host.config(hosts=arguments.NAMES,
                        ips=arguments.IPS,
                        username=arguments.user,
                        key=key)
            print (result)

        elif arguments.check:

            key = arguments.key or "~/.ssh/id_rsa.pub"
            result = Host.check(hosts=arguments.NAMES,
                                username=arguments.user,
                                key=key)
            for entry in result:
                entry['success'] = entry['stdout'] == entry['host']

            _print(result)

        elif arguments.tunnel and arguments.create:

            wlan_ip = Shell.run("hostname -I | awk '{print $2}'").strip()
            print(f'\nUsing wlan0 IP = {wlan_ip}')
            hostname = Shell.run("hostname").strip()
            print(f'Using cluster hostname = {hostname}')

            names = Parameter.expand(arguments.NAMES)
            port = arguments.port or "8001"
            ssh_config_output = ""

            for name in names:
                service_name = f"autossh-{name}.service"

                service_template = "[Unit]\n" \
                f"Description=AutoSSH tunnel service to {name} on local port " \
                                   f"{port}\n" \
                "After=network.target\n\n" \
                "[Service]\n" \
                "User=pi\n" \
                "Group=pi\n" \
                'Environment="AUTOSSH_GATETIME=0"\n' \
                'ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" '\
                                   '-o "ServerAliveCountMax 3" -i ' \
                                   '/home/pi/.ssh/id_rsa -NL ' \
                                   f'{wlan_ip}:{port}:localhost:22 p' \
                                   f'i@{name}\n\n'\
                "[Install]\n" \
                "WantedBy=multi-user.target"

                ssh_config_template = f'Host {name}\n' \
                                      f'     HostName {hostname}.local\n' \
                                      f'     User pi\n' \
                                      f'     Port {port}\n\n'


                ssh_config_output += ssh_config_template
                sudo_writefile(f'/etc/systemd/system/{service_name}',
                               service_template)
                port = str(int(port) + 1)

            os.system('sudo systemctl daemon-reload')
            for name in names:
                servicename = f"autossh-{name}.service"
                os.system(f'sudo systemctl start {servicename}')
                os.system(f'sudo systemctl enable {servicename}')

            print('\nTunnels created.\n\nPlease place the following in your '
                  'remote machine\'s (i.e. laptop) ~/.ssh/config file to '
                  'alias simple ssh access (i.e. ssh red001).')
            banner('copy to ~/.ssh/config on remote host (i.e laptop)')
            print(ssh_config_output)

        return ""
