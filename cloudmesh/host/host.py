from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile, writefile
import os
from glob import glob
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Host import Host as CommonHost
from cloudmesh.common.util import banner
from pprint import pprint

class Host(CommonHost):

    @staticmethod
    def os_ssh(names, command, dryrun=False):
        for name in names:
            executor = f"ssh {name} {command}"
            print()
            print (executor)
            os.system(executor)
            print()

    @staticmethod
    def ssh(hosts=None,
            command=None,
            username=None,
            key="~/.ssh/id_rsa.pub",
            shell=False,
            processors=3,
            dryrun=False,
            executor=None,
            verbose=False):

        if type(hosts) == list:
            joined = ','.join(hosts)

        result = CommonHost.ssh(hosts=joined,
                                command=command,
                                username=None,
                                key=key,
                                shell=shell,
                                processors=processors,
                                dryrun=dryrun,
                                executor=None,
                                verbose=verbose)

        return result

    @staticmethod
    def gather(user,
               names,
               source,
               destination="~/.ssh/authorized_keys",
               dryrun=False,
               append=False,
               tmp=None):
        """

        please note this is not used as we have a temporary better
        implemnetation in command.

        :param user:
        :param names:
        :param source:
        :param destination:
        :param dryrun:
        :param append:
        :param tmp:
        :return:
        """

        if type(names) != list:
            _names = Parameter.expand(names)

        tmp_dir = tmp or path_expand("~/.cloudmesh/tmp")
        Shell.mkdir(tmp_dir)

        destinations = []
        for name in _names:
            destinations.append("{name}:{file}")

        directory = os.path.dirname(destination)
        Shell.mkdir(directory)

        if not append:
            Shell.rm(path_expand(destination))
            writefile(destination, "")

        for name in _names:
            source = f"{user}@{name}:{destination}"
            print(f"{source} -> {tmp_dir}/{destination}")
            result = Host.scp(source, f"{tmp_dir}/{destination}-{name}", dryrun)

        with open(path_expand(destination), 'a') as file:
            for filename in glob(tmp_dir):
                content = readfile(filename)
                file.write(content)


    @staticmethod
    def scatter(user=None,
                hosts=None,
                source=None,
                processors=3,
                destination="~/.ssh/authorized_keys",
                dryrun=False):


        if type(hosts) == list:
            joined = ','.join(hosts)
        else:
            joined = hosts

        command = "mkdir -p .ssh"
        print ("H", hosts)


        results = CommonHost.ssh(hosts=joined,
                                command=command,
                                username=None,
                                processors=processors)

        pprint (results)

        names = Parameter.expand(joined)

        for name in names:

            if user:
                _destination = f"{user}@{name}:{destination}"
            else:
                _destination = f"{name}:{destination}"

            print (f"{source} -> {_destination}")
            Host.scp(source, _destination, dryrun)

    @staticmethod
    def scp(source, destination, output="lines", dryrun=False):
        """

        :param names:
        :param command:
        :param output:
        :return:
        """

        command = (f"scp  {source} {destination}")
        if not dryrun:
            result = Shell.run(command)

        return result

    @staticmethod
    def concatenate_keys(results):
        result = ""
        for entry in results:
            name, key = entry
            key = ''.join(key)
            result += str(key) + '\n'
        result = result.strip()
        return result

    """
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
    """
