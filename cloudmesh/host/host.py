from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile, writefile
import os
from glob import glob
from cloudmesh.common.parameter import Parameter

class Host(object):

    # noinspection PyPep8
    @staticmethod
    def ssh(user, names, command, output="lines", dryrun=False):
        """
        Executes the command on the hosts specified by the hosts given in the names list

        :param user: the username
        :param names: the list of the names of the hosts
        :param command: the command to be executed
        :param output: the output returned as list
        :return: a list of tuples of the form (name, result) where the
                 output is in result and if splitlines is specified the result
                 is a ist

        Example:

            cms host ssh red[01-03] "cat ~/.ssh/authorized_keys"


        """
        if type(names) != list:
            names = Parameter(names)

        results = []

        for name in names:
            _command = command.format(name=name)

            _command = f"ssh {user}@{name} {_command}"
            if dryrun:
                print(_command)
            else:
                result = Shell.run(_command)

                if output == "lines":
                    lines = result.splitlines()
                    results.append((name, lines))
                elif output == "string":
                    results.append((name, result))

        return results

    @staticmethod
    def gather(user,
               names,
               source,
               destination="~/.ssh/authorized_keys",
               dryrun=False,
               append=False,
               tmp=None):

        if type(names) != list:
            names = Parameter(names)

        tmp_dir = tmp or path_expand("~/.cloudmesh/tmp")
        Shell.mkdir(tmp_dir)

        destinations = []
        for name in names:
            destinations.append("{name}:{file}")

        directory = os.path.dirname(destination)
        Shell.mkdir(directory)

        if not append:
            Shell.rm(path_expand(destination))
            writefile(destination, "")

        for name in names:
            source = f"{user}@{name}:{destination}"
            print(f"{source} -> {tmp_dir}/{destination}")
            result = Host.scp(source, f"{tmp_dir}/{destination}-{name}", dryrun)

        with open(path_expand(destination), 'a') as file:
            for filename in glob(tmp_dir):
                content = readfile(filename)
                file.write(content)


    @staticmethod
    def scatter(user,
                names,
                source,
                destinaton="~/.ssh/authorized_keys",
                dryrun=False):

        if type(names) != list:
            names = Parameter(names)

        for name in names:
            directory = os.path.dirname(destination)
            Host.ssh(f"{user}@{name}", f"mkdir -p directory", dryrun)

            destination = f"{user}@{name}:{destination}"
            print (f"{source} -> {destination}")
            Host.scp(source, destination, dryrun)

    @staticmethod
    def generate_key(user,
                     names,
                     output="lines",
                     dryrun=False):

        for name in names:
            Host.ssh(f"{user}@{name}", f'cat /dev/zero | ssh-keygen -t rsa -b 4096 -q -P ""', dryrun)


    # cat ~/.ssh/id_rsa.pub | ssh {user}@{ip} "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >>  ~/.ssh/authorized_keys"

    @staticmethod
    def scp(source, destinations, output="lines", dryrun=False):
        """

        :param names:
        :param command:
        :param output:
        :return:
        """

        results = []
        for destination in destinations:
            command = (f"scp  {source} {destination}")
            # result = command.format(name=name)

            print(command)

            if not dryrun:
                result = Shell.run(command)

                if output == "lines":
                    lines = result.splitlines()
                    results.append((destination, lines))
                elif output == "string":
                    results.append((destination, result))

        return results

    @staticmethod
    def concatenate_keys(results):
        result = ""
        for entry in results:
            name, key = entry
            key = ''.join(key)
            result += str(key) + '\n'
        result = result.strip()
        return result

    @staticmethod
    def fix_keys_file(filename):
        # concatenate ~/.ssh/id_rsa.pub
        lines = readfile(filename)
        key = readfile(path_expand("~/.ssh/id_rsa.pub"))

        authorized_keys = lines + key
        keys = ''.join(authorized_keys)

        # remove duplicates and empty lines
        keys_list = [x for x in list(set(keys.splitlines())) if x != '\n']
        keys = ('\n'.join(keys_list) + '\n')

        writefile(filename, str(keys))
