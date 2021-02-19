import os
from cloudmesh.common.console import Console


class HostCreate:

    @staticmethod
    def setup(workers, laptop):

        remote_host = laptop
        remote_hostname = remote_host.split('@')[1]

        Console.info("Setting up eth to wifi bridge.")
        os.system("cms bridge create --interface='wlan0'")
        Console.info("Creating keys on workers")
        os.system(f"cms host key create {workers}")
        Console.info(f"Gathering keys from workers, and remote host. Please input"
                     f" {remote_host} password if requested.")
        os.system(f"ping -c 4 {remote_hostname}")  # best to resolve before ssh
        os.system(f"cms host key gather {workers},{remote_host} "
                  f"~/.ssh/authorized_keys")
        Console.info("Scattering keys to manager and workers.")
        os.system(f"cms host key scatter {workers} ~/.ssh/authorized_keys")
        Console.info("Setting up ssh tunnels to workers through manager")
        os.system(f"cms host tunnel create {workers}")
