import os
import platform

from pprint import pprint
from getpass import getpass
import textwrap

from cloudmesh.common.Host import Host
from cloudmesh.common.Printer import Printer
from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import yn_choice
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.util import str_bool
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command
from cloudmesh.shell.command import map_parameters
from cloudmesh.host.HostCreate import HostCreate
from cloudmesh.common.sudo import Sudo


class HostCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_host(self, args, arguments):
        """
        ::

          Usage:
              host scp NAMES SOURCE DESTINATION [--dryrun]
              host ssh NAMES COMMAND [--dryrun] [--output=FORMAT]
              host config NAMES --ips=IPS [--user=USER] [--key=PUBLIC]
              host config --proxy=PROXY NAMES [--user=USER] [--append] [--local=no] [--StrictHostKeyChecking=no] [--cluster=name]
              host config NAMES [--user=USER] [--append] [--local=no] [--StrictHostKeyChecking=no] [--cluster=name]
              host find [NAMES] [--user=USER] [--table|--json] [--verbose]
              host check NAMES [--user=USER] [--key=PUBLIC]
              host key create NAMES [--user=USER] [--dryrun] [--output=FORMAT]
              host key list NAMES [--output=FORMAT]
              host key setup NAMES
              host key gather NAMES [--authorized_keys] [FILE]
              host key scatter NAMES [FILE] [--user=USER]
              host key add NAMES [FILE]
              host key delete NAMES [FILE]
              host key access NAMES [FILE] [--user=USER]
              host tunnel create NAMES [--port=PORT]
              host mac NAMES [--eth] [--wlan] [--output=FORMAT]
              host setup WORKERS [LAPTOP]
              host shutdown NAMES
              host reboot NAMES
              host adduser NAMES USER
              host passwd NAMES USER
              host addsudo NAMES USER
              host deluser NAMES USER
              host ping NAMES
              host info NAMES


          This command does some useful things.

          Arguments:
              FILE   a file name

          Options:
              --dryrun         shows what would be done but does not execute
              --output=FORMAT  the format of the output
              --port=PORT      starting local port for tunnel assignment
              --local=no       do not append .local to manager hostname [default: yes]
              --user=USER      username for manager and workers [default: pi]
              --ips=IPS        ip addresses of the manager and workers
              --StrictHostKeyChecking=no  if set to yes, strict host checking is enforced [default: no]
              --ProxyJump=no  if set to yes, a proxyjump is performed for each worker through the manager [default: yes]

          Description:

              host scp NAMES SOURCE DESTINATION

                Uses scp to transfer Source to NAMES:DESTINATION.

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

              host key scatter HOSTS FILE [--user=USER]

                copies all keys from file FILE to authorized_keys on all hosts,
                but also makes sure that the users ~/.ssh/id_rsa.pub key is in
                the file. If provided the optional user, it will add the keys to
                that user's .ssh directory. This is often required when
                adding a new user in which case HOSTS should still a sudo
                user with ssh currently enabled.

                1) adds ~/.id_rsa.pub to the FILE only if its not already in it
                2) removes all duplicated keys

                Example:
                    ssh key scatter "red[01-10]"
                    ssh key scatter pi@red[01-10] keys.txt --user=alice

              host key add NAMES FILE

                Adds all keys in FILE into the authorized_keys of NAMES.

                Example:
                    cms host key add worker001 ~/.ssh/id_rsa.pub

              host key delete NAMES FILE

                Deletes all keys in fILE from authorized_keys of NAMES if they exist.

                Example
                    cms host key delete worker001 ~/.ssh/id_rsa.pub

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

              host mac NAMES

                returns the list of mac addresses of the named pis.

              host setup WORKERS [LAPTOP]

                Executes the following steps

                    cms bridge create --interface='wlan0'
                    cms host key create red00[1-3]
                    cms host key gather red00[1-3],you@yourlaptop.local keys.txt
                    cms host key scatter red00[1-3],localhost keys.txt
                    rm keys.txt
                    cms host tunnel create red00[1-3]

              host shutdown NAMES

                Shutsdown NAMES with `sudo shutdown -h now`. If localhost in
                names, it is shutdown last.

              host reboot NAMES

                Reboots NAMES with `sudo reboot`. If localhost in names,
                it is rebooted last.

              host adduser NAMES USER

                Adds a user with user name USER to the hosts identified by
                NAMES. Password is disabled, see host passwd to enable.

              host addsudo NAMES USER

                Adds sudo rights to USER at NAMES

              host passwd NAMES USER

                Changes the password for USER at NAMES

              host deluser NAMES USER

                Deleted USER from NAMES. Home directory will be removed.

              host config proxy PROXY NAMES

                This adds to your ~/.ssh/config file a ProxyJump
                configuration to reach NAMES via PROXY. This is useful when
                the PROXY is acting as a network bridge for NAMES to your
                current device.

                Example:
                    cms host config proxy pi@red.lcaol red00[1-2]
        """

        def _print(results):
            arguments.output = arguments.output or 'table'

            if arguments.output in ['table', 'yaml']:
                print(Printer.write(results,
                                    order=['host', 'success', 'stdout', 'stderr'],
                                    output=arguments.output))
            else:
                pprint(results)

        def _print_pis(results):
            arguments.output = arguments.output or 'table'

            if arguments.output in ['table', 'yaml']:
                print(Printer.write(results,
                                    order=['name', 'ip', 'user', 'os', 'mac', 'model', 'memory', 'serial', ".local"],
                                    output=arguments.output))
                # not printed         "revision"
                # not printed         "hardware"
            else:
                pprint(results)


        def get_filename(filename, hosts):
            if filename is not None:
                return filename
            if type(hosts) == str:
                hosts = Parameter.expand(hosts)
            label = hosts[0]
            return path_expand(f"~/.ssh/cluster_keys_{label}")

        map_parameters(arguments,
                       'eth',
                       'wlan'
                       'dryrun',
                       'output',
                       'user',
                       'port',
                       'append',
                       'StrictHostKeyChecking',
                       'local',
                       'proxy',
                       'ips',
                       'cluster'
                       )
        dryrun = arguments.dryrun

        # VERBOSE(arguments)

        if dryrun:
            VERBOSE(arguments)

        if arguments.info:

            names = Parameter.expand(arguments.names)

            # check if .local
            # check if mesh network
            # check if static network

            # use arp - a di find hosts ips
            # if linux
            #    dig +short -x  192.168.50.1

            Console.error("Not yet Implemented")

        elif arguments.find:

            verbose = arguments["--verbose"]

            names = Parameter.expand(arguments.NAMES)

            # temporary so we can easy modify while not needing to update cloudmesh.common
            from cloudmesh.host.network import PiNetwork

            network = PiNetwork()

            pis = network.find_pis(user=arguments.user, verbose=verbose)
            if arguments["--json"]:
                print(pis)
            else:
                _print_pis(pis)

        elif arguments.mac:

            names = Parameter.expand(arguments.NAMES)

            if not arguments.eth and not arguments.wlan:
                arguments.eth = True
                arguments.wlan = True

            eth = 'cat /sys/class/net/eth0/address'
            wlan = 'cat /sys/class/net/wlan0/address'
            if arguments.eth:
                results = Host.ssh(hosts=names, command=eth, username=arguments.user)
                print("eth0:")
                _print(results)

            if arguments.wlan:

                results = Host.ssh(hosts=names, command=wlan, username=arguments.user)
                print("wlan0:")
                _print(results)

        elif arguments.setup:

            HostCreate.setup(workers=arguments.WORKERS, laptop=arguments.LAPTOP)

        elif arguments.scp and not arguments.key:

            result = Host.put(
                hosts=arguments.NAMES,
                source=arguments.SOURCE,
                destination=arguments.DESTINATION
            )

            _print(result)

        elif arguments.ping:
            names = Parameter.expand(arguments.NAMES)

            # print (names)

            results = Host.ping(hosts=names)

            _print(results)

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

        elif arguments.key and arguments.add:
            filename = get_filename(arguments.NAMES)
            if not os.path.isfile(filename):
                Console.error(f"Cannot find file {filename}")
                return

            # Copy to temp location
            Host.put(
                hosts=arguments.NAMES,
                source=filename,
                destination="~/.ssh/key.tmp"
            )
            # Execute append command and remove command
            command = 'cat ~/.ssh/key.tmp >> ~/.ssh/authorized_keys && rm ~/.ssh/key.tmp'
            Host.ssh(
                hosts=arguments.NAMES,
                command=command
            )

        elif arguments.key and arguments.delete:
            Console.ok("key delete")
            filename = get_filename(arguments.FILE, arguments.NAMES)
            if not os.path.isfile(filename):
                Console.error(f"Cannot find file {filename}")
                return
            # Copy to temp location
            remote_temp = "~/.ssh/key.tmp"
            Host.put(
                hosts=arguments.NAMES,
                source=filename,
                destination=remote_temp
            )
            # grep can read multiple patterns from a file, one per line. Combine with
            # the options -v to output non-matching lines, and -F to match strings
            # instead of regex and -x to require that the whole line matches.
            command = f"""grep -Fvx -f {remote_temp} ~/.ssh/authorized_keys >remaining_keys && \
            mv remaining_keys ~/.ssh/authorized_keys && \
            rm {remote_temp}"""
            Host.ssh(
                hosts=arguments.NAMES,
                command=command
            )
            Console.ok(f"Delete keys from {filename} on {arguments.NAMES}")


        elif arguments.key and arguments.setup:

            label = Parameter.expand(arguments.NAMES)[0]
            filename = get_filename(arguments.FILE, arguments.NAMES)
            directory = os.path.dirname(filename)

            if directory:
                Shell.mkdir(directory)

            output = Host.gather_keys(
                username=arguments.user,
                hosts=arguments.NAMES,
                filename="~/.ssh/id_rsa.pub",
                key="~/.ssh/id_rsa",
                processors=3,
                dryrun=False)

            with open(filename, "w") as f:
                f.write(output)

            # scatter
            # place .ssh/config a trict host check to no

        elif arguments.key and arguments.gather:

            output = Host.gather_keys(
                username=arguments.user,
                hosts=arguments.NAMES,
                filename="~/.ssh/id_rsa.pub",
                key="~/.ssh/id_rsa",
                processors=3,
                dryrun=False)

            VERBOSE(arguments)

            filename = get_filename(arguments.FILE, arguments.NAMES)

            print(output)

            banner(f"Writing Keys to file {filename}")

            directory = os.path.dirname(filename)
            print('command directory', directory)
            if directory:
                Shell.mkdir(directory)

            if os.path.isfile(filename) and yn_choice(f'{filename} is not empty. Do you wish to overwrite it? (If no you will append).'):
                with open(filename, "w") as f:
                    f.write(output)
            else:
                with open(filename, "a") as f:
                    f.write(output)

        elif arguments.key and arguments.scatter:

            #
            # this should be a function in Host
            #


            filename = get_filename(arguments.FILE, arguments.NAMES)

            names = arguments.NAMES
            user = arguments.user

            if not os.path.isfile(filename):
                Console.error("The file does not exist")
                return ""

            if not user:
                result = Host.put(hosts=names,
                                  source=filename,
                                  destination=".ssh/authorized_keys")

                _print(result)
            else:
                Console.info('SCP to ./temp_authorzied_keys_temp')
                result = Host.put(hosts=names,
                                  source=filename,
                                  destination="temp_authorized_keys_temp")
                _print(result)

                Console.info(f'Mkdir /home/{user}/.ssh if not exist')
                command = f'sudo mkdir -p /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info(f'Chown /home/{user}/.ssh to {user}')
                command = f'sudo chown {user}:{user} /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info(f'Chmod /home/{user}/.ssh to 700')
                command = f'sudo chmod 700 /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info(f'Mv temp_authorized_keys_temp to /home/'
                             f'{user}/.ssh/authorized_keys')
                command = f'sudo mv temp_authorized_keys_temp /home/' \
                          f'{user}/.ssh/authorized_keys'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info(f'Chown /home/{user}/.ssh/authorized_keys to '
                             f'{user}')
                command = f'sudo chown {user}:{user} /home/' \
                          f'{user}/.ssh/authorized_keys'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

        elif arguments.key and arguments.access:

            #
            # this should be a function in Host
            #

            names = arguments.NAMES
            user = arguments.user

            filename = arguments.FILE
            temp = path_expand("~/.cloudmesh/temp_config")

            if filename:
                config = readfile(filename)
            else:
                config = textwrap.dedent("""
                Host *
                    StrictHostKeyChecking no
                """).strip()
            writefile(temp,config)

            if not os.path.isfile(temp):
                Console.error("The file does not exist")
                return ""

            if not user:
                result = Host.put(hosts=names,
                                  source=temp,
                                  destination=".ssh/config")

                _print(result)
            else:
                Console.info(f'Mkdir /home/{user}/.ssh if not exist')
                command = f'sudo mkdir -p /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info('SCP to ./temp_config')
                result = Host.put(hosts=names,
                                  source=temp,
                                  destination=".ssh/config")
                _print(result)

                Console.info(f'Chown /home/{user}/.ssh to {user}')
                command = f'sudo chown {user}:{user} /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)

                Console.info(f'Chmod /home/{user}/.ssh to 700')
                command = f'sudo chmod 700 /home/' \
                          f'{user}/.ssh/'
                result = Host.ssh(hosts=names,
                                  command=command)
                _print(result)


        elif arguments.config and arguments.ips:

            print ("NNNNNNNN")

            key = arguments.key or "~/.ssh/id_rsa.pub"
            result = Host.config(hosts=arguments.NAMES,
                                 ips=arguments.IPS,
                                 username=arguments.user,
                                 key=key)
            print(result)

            """
            host config NAMES --ips=IPS [--user=USER] [--key=PUBLIC]
            host config --proxy=PROXY NAMES [--user=USER] [--append] [--local=no] [--StrictHostKeyChecking=no]
            host config NAMES [--user=USER] [--append] [--local=no] [--StrictHostKeyChecking=no]
            """

        elif arguments.config:

            if str_bool(arguments.local):
                local_str = ".local"
            else:
                local_str = ""

            if str_bool(arguments.StrictHostKeyChecking):
                strict_host_str = "yes"
            else:
                strict_host_str = "no"

            names = Parameter.expand(arguments.NAMES)
            user = arguments.user
            if arguments.cluster:
                cluster = arguments.cluster
            else:
                # take the first name and remove spaces
                cluster = ''.join([i for i in names[0] if not i.isdigit()])


            ssh_config_output = ""
            ssh_config_output = f'\n##### CLOUDMESH PROXY CONFIG {cluster} #####\n\n'

            if arguments.proxy:
                proxy_host = arguments.proxy
                proxy_jump = f'     ProxyJump {proxy_host}\n'
                ssh_config_output += \
                                    f'Host {proxy_host}\n' \
                                    f'     HostName {proxy_host}{local_str}\n' \
                                    f'     User {user}\n' \
                                    f'     PreferredAuthentications publickey\n' + \
                                    f'     StrictHostKeyChecking {strict_host_str}\n'
                ssh_config_output += '\n'

            else:
                proxy_jump = ""


            """
            ssh_config_output = f'\n##### CLOUDMESH PROXY CONFIG {cluster} #####\n\n'\
                                f'Host {proxy_host}\n' \
                                f'     HostName {proxy_host}{local_str}\n' \
                                f'     User {user}\n' \
                                f'     StrictHostKeyChecking {strict_host_str}\n\n'
            """

            ### the local_str in the hostname may be wrong since its not manager
            for name in names:
                ssh_config_template = f'Host {name}\n' \
                                      f'     HostName {name}{local_str}\n' \
                                      f'     User {user}\n' \
                                      f'     PreferredAuthentications publickey\n' + \
                                      f'     StrictHostKeyChecking {strict_host_str}\n' + \
                                      proxy_jump

                ssh_config_template += '\n'

                ssh_config_output += ssh_config_template

            ssh_config_output += f'##### CLOUDMESH PROXY CONFIG {cluster} #####\n'

            print('Adding to ~/.ssh/config')
            print(ssh_config_output)

            if not os.path.exists(path_expand('~/.ssh/config')):
                with open(path_expand('~/.ssh/config'), 'w+') as f:
                    f.write(ssh_config_output)
            else:
                f = open(path_expand('~/.ssh/config'), 'r')
                lines = f.readlines()
                f.close()
                with open(path_expand('~/.ssh/config'), 'w+') as f:
                    if f'##### CLOUDMESH PROXY CONFIG {cluster} #####\n' in lines:
                        start = lines.index(f'##### CLOUDMESH PROXY CONFIG {cluster} #####\n')
                        lines.reverse()
                        end = lines.index(f'##### CLOUDMESH PROXY CONFIG {cluster} #####\n')
                        end = len(lines) - end - 1
                        lines.reverse()
                        original_config = lines[start:end + 1]
                        del lines[start:end + 1]
                        f.writelines(lines)
                        if arguments.append:
                            f.writelines(original_config)
                            f.write(ssh_config_output)
                        else:
                            f.write(ssh_config_output)
                    else:
                        f.writelines(lines)
                        f.write(ssh_config_output)
                        f.close()


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
            ssh_config_output = f'Host {hostname}\n' \
                                f'     HostName {hostname}.local\n' \
                                f'     User pi\n\n'

            for name in names:
                service_name = f"autossh-{name}.service"

                service_template = "[Unit]\n" \
                                   f"Description=AutoSSH tunnel service to {name} on local port " \
                                   f"{port}\n" \
                                   "After=multi-user.target\n\n" \
                                   "[Service]\n" \
                                   "User=pi\n" \
                                   "Group=pi\n" \
                                   'Environment="AUTOSSH_GATETIME=0"\n' \
                                   'ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" ' \
                                   '-o "ServerAliveCountMax 3" -i ' \
                                   '/home/pi/.ssh/id_rsa -NL ' \
                                   f'{wlan_ip}:{port}:localhost:22 p' \
                                   f'i@{name}\n\n' \
                                   "[Install]\n" \
                                   "WantedBy=multi-user.target"

                ssh_config_template = f'Host {name}\n' \
                                      f'     HostName {hostname}.local\n' \
                                      f'     User pi\n' \
                                      f'     Port {port}\n\n'

                ssh_config_output += ssh_config_template
                Sudo.writefile(f'/etc/systemd/system/{service_name}',
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

        elif arguments.shutdown or arguments.reboot:

            if arguments.shutdown:
                command = 'sudo shutdown -h now'
            elif arguments.reboot:
                command = 'sudo reboot'

            names = Parameter.expand(arguments.NAMES)
            hostname = Shell.run("hostname").strip()

            localhost = None
            if "localhost" in names:
                names.remove("localhost")
                localhost = True
            if hostname in names:
                names.remove(hostname)
                localhost = True

            manager, workers = Host.get_hostnames(names)

            if workers:
                Console.info(f'Executing `{command}` for {workers}')
                Host.ssh(hosts=workers, command=command)

            if manager:
                Console.info(f'Executing `{command}` for {manager}')
                Host.ssh(hosts=manager, command=command)

            #_print(results)
            # results can be misleading becuase there is a race between the
            # shutdown and the error code being returned from the ssh processes.

            if localhost:
                os.system(command)

        elif arguments.adduser:
            names = Parameter.expand(arguments.NAMES)
            user = arguments.USER

            localhost = None
            if 'localhost' in names:
                localhost = 'localhost'
            elif platform.node() in names:
                localhost = platform.node()

            if localhost in names:
                print('\nAdding user to localhost')
                result = Shell.run(f'sudo adduser {user} '
                                   f'--disabled-password '
                                   f'--gecos "" ')
                print(result)
                names.remove(localhost)

            if len(names) > 0:
                command = f"sudo adduser {user} --disabled-password --gecos ',' "
                results = Host.ssh(
                    hosts=names,
                    command=command
                )
                _print(results)

        elif arguments.passwd:
            names = Parameter.expand(arguments.NAMES)
            user = arguments.USER

            localhost = None
            if 'localhost' in names:
                localhost = 'localhost'
            elif platform.node() in names:
                localhost = platform.node()

            if localhost in names:
                print("\nSetting password on localhost, please provide user "
                      "password")
                result = os.system(f'sudo passwd {user}')
                print(result)
                names.remove(localhost)

            if len(names) > 0:
                print("\nSetting password on remote hosts, please enter user "
                      "password\n")
                password = getpass("Please enter the user password:")

            if len(names) > 0:
                command = f'echo -e "{password}\n{password}" | sudo passwd {user}'
                results = Host.ssh(
                    hosts=names,
                    command=command
                )
                _print(results)

        elif arguments.addsudo:
            names = Parameter.expand(arguments.NAMES)
            user = arguments.USER

            localhost = None
            if 'localhost' in names:
                localhost = 'localhost'
            elif platform.node() in names:
                localhost = platform.node()

            if localhost in names:
                print('\nAdding user to sudo group on localhost')
                result = Shell.run(f'sudo adduser {user} sudo')
                print(result)
                names.remove(localhost)

            if len(names) > 0:
                command = f'sudo adduser {user} sudo'
                results = Host.ssh(
                    hosts=names,
                    command=command
                )
                _print(results)

        elif arguments.deluser:
            names = Parameter.expand(arguments.NAMES)
            user = arguments.USER

            if 'localhost' in names:
                localhost = 'localhost'
            elif platform.node() in names:
                localhost = platform.node()

            if localhost in names:
                print('\nDeleting user on localhost')
                result = Shell.run(f'sudo userdel -r {user}')
                print(result)
                names.remove(localhost)

            if len(names) > 0:
                command = f'sudo userdel -r {user}'
                results = Host.ssh(
                    hosts=names,
                    command=command
                )
                _print(results)



        return ""
