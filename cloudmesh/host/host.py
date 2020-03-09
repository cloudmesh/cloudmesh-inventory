from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile, writefile
import os
from glob import glob
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.Host import Host as CommonHost

class Host(object):

    @staticmethod
    def gather(user,
               names,
               source,
               destination="~/.ssh/authorized_keys",
               dryrun=False,
               append=False,
               tmp=None):

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
    def scatter(user,
                names,
                source,
                destinaton="~/.ssh/authorized_keys",
                dryrun=False):

        if type(names) != list:
            _names = Parameter.expand(names)

        for name in _names:
            directory = os.path.dirname(destination)
            Host.ssh(f"{user}@{name}", f"mkdir -p directory", dryrun)

            destination = f"{user}@{name}:{destination}"
            print (f"{source} -> {destination}")
            Host.scp(source, destination, dryrun)

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
