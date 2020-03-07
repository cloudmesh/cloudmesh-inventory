from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile, writefile


class Host(object):

    # noinspection PyPep8
    @staticmethod
    def ssh(names, command, output="lines", dryrun=False):
        """

        :param names:
        :param command:
        :param output:
        :return:

        Advanced usage:

        cms host ssh red[01-03] \"cat /Users/grey/Desktop/github/cloudmesh-community/cm/fa19-516-158/cluster/{name}/authorized_keys\"

        """

        results = []

        for name in names:
            _command = command.format(name=name)

            _command = f"ssh {name} {_command}"
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
    def gather(names, file, desitnation, dryrun=False):

        sources = []
        for name in names:
            sources.append("{name}:{file}")

        # mkddir -p destinat dir
        # create desination s we can append

        for source in sources:
            print (f"{source}/{file}")
            # content = Host.get(source, file)
            # destination="~/.ssh/authorized_keys")

        raise NotImplementedError

    @staticmethod
    def scatter(names, source, destinaton="~/.ssh/authorized_keys", dryrun=False):

        destinations = []
        for name in names:
            destinations.append("{name}:{file}")

        # mkddir -p destinat dir
        # create desination s we can append

        for destination in destinations:
            print (f"{source}/{destination}")
            # content = Host.get(source, file)
            # destination="~/.ssh/authorized_keys")


        #Host.scp_new(file, destination="~/.ssh/authorized_keys")

        raise NotImplementedError



    @staticmethod
    def put(source, destination, output="lines", dryrun=False):
        """

        :param names:
        :param command:
        :param output:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def get(source, destination, output="lines", dryrun=False):
        """

        :param names:
        :param command:
        :param output:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def generate_key(names, output="lines", dryrun=False):

        raise NotImplementedError

        Host.ssh(names)


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
