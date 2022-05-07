from cloudmesh.common.Shell import Shell
from cloudmesh.common.console import Console

class PiNetwork:

    def __int__(self):
        self.verbose = False

    def arp(self):
        """
        Finds the ips in the network

        Returns: list of ips in the network
        """
        ips = []
        lines = Shell.run("arp -a").strip().splitlines()
        for line in lines:
            if "(" in line:
                ip = line.split("(")[1].split(")")[0]
                ips.append(ip)
        return ips

    def find_pis(self, user="pi", verbose=False):
        self.verbose = verbose
        data = []
        ips = self.arp()
        for ip in ips:
            if self.verbose:
                print (ip, user)
            found = self.is_pi4(ip, user=user)
            if found:
                data.append(found)
        return data

    def _ssh(self, command, timeout=1):
        _command = f"ssh -o ConnectTimeout={timeout} -o StrictHostKeyChecking=no {command}"
        # print (_command)
        r = Shell.run(_command).strip()
        return r

    def is_pi4(self, ip, user="pi"):
        r = self._ssh(f"{user}@{ip} ip a")
        if "Connection timed out" in r:
            if self.verbose:
                Console.error(f"{user}@{ip} Timeout")
            r = None
        elif "Connection refused" in r:
            if self.verbose:
                Console.error(f"{user}@{ip} refused")
            r = None
        if r is None:
            return r

        # check mac address
        data = {
            "mac": None,
            "name": None,
            "user": user,
            "os": None,
            "pi": None,
            "model": None,
            "ip": ip,
            "revision": None,
            "serial": None,
            "memory": None,
            "hardware": None,
            ".local": None
        }

        if "dc:a6:32" in r:
            data["pi"] = True
        data["mac"] = self._ssh(f"{user}@{ip} cat /sys/class/net/eth0/address")
        name= data["name"] = self._ssh(f"{user}@{ip} hostname")
        data["model"] = self._ssh(f"{user}@{ip} cat /sys/firmware/devicetree/base/model").replace("\x00", "")\
            .replace("Raspberry ", "").replace("Model ", "").replace("Rev ","")
        data["serial"] = self._ssh(f"{user}@{ip} cat /sys/firmware/devicetree/base/serial-number").replace("\x00", "")
        data["memory"] = self._ssh(f"{user}@{ip} free -h -t | fgrep Total:").split("Total:")[1].strip().split(" ")[0]
        os_version = self._ssh(f"{user}@{ip} cat /etc/os-release")
        data["os"] = Shell.cm_grep(os_version, "VERSION=")[0].split("=")[1].replace('"',"")

        cpuinfo = self._ssh(f"{user}@{ip} cat /proc/cpuinfo").replace("\t", "")
        data["revision"] = Shell.cm_grep(cpuinfo, "Revision")[0].split(":")[1]
        data["hardware"] = Shell.cm_grep(cpuinfo, "Hardware")[0].split(":")[1]

        find_local = self._ssh(f"{user}@{name}.local hostname")
        data[".local"] = find_local == name


        return data





