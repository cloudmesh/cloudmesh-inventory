###############################################################
# pytest -v --capture=no  tests/test_host.py::Test_host.test_001
# pytest -v --capture=no  tests/test_host.py
# pytest -v tests/test_host.py
###############################################################

from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.host.host import Host
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.console import Console
import pytest
import sys

config_hosts = """

Host red01
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa.pub

Host red02
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa.pub

Host red03
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa.pub

"""


@pytest.mark.incremental
class Test_host:

    def setup(self):
        self.host = Host()

    def test_ssh_config(self):
        HEADING()

        try:
            names = Parameter.expand("red[01-03]")
            for name in names:
                banner(name)
                result = self.host.ssh(name,"uname")
                print (result)
                assert result[0][1] is not None

        except Exception as e:
            Console.error("Make sure you have the following in your ~/.ssh/config")
            print (config_hosts)
            Console.error(
                "Make sure you have the ssh remote login enabled")
            print (e)
            Console.error("Your computer is not properly set up to do the test")
            sys.exit()


    def test_ssh_keygen(self):
        HEADING()

        names = Parameter.expand("red[01-03]")
        for name in names:
            banner(name)
            result = self.host.generate_key(name,filename=f"~/.ssh/id_rsa_{name}", dryrun=False)
            print (result)



