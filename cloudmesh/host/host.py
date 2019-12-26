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
                    lines = result.split("\n")
                    results.append((name, lines))
                elif output == "string":
                    results.append((name, result))

        return results

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
                    lines = result.split("\n")
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
