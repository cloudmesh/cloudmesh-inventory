from cloudmesh.common.Shell import Shell
from pprint import pprint

class Host (object):

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

            print(f"ssh {name} {_command}")

            if not dryrun:
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

            print (command)

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
            key = ' '.join(key)
            result = result + str(key) + "\n"
        result = result.strip()
        return result
