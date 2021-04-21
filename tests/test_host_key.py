###############################################################
# pytest -v --capture=no  tests/test_host.py::Test_host.test_001
# pytest -v --capture=no  tests/test_host.py
# pytest -v tests/test_host.py
###############################################################

import os
import sys
from pprint import pprint

import pytest
from cloudmesh.common.Host import Host as CommonHost
from cloudmesh.common.console import Console
from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.common.util import path_expand
from cloudmesh.host.host import Host

config_hosts = """

Host red01
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa

Host red02
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa

Host red03
    StrictHostKeyChecking no
    Hostname 127.0.0.1
    IdentityFile ~/.ssh/id_rsa

"""


@pytest.mark.incremental
class Test_host:

    def setup(self):
        self.host = Host()

    def test_ping(self):
        HEADING()

        try:
            result = CommonHost.ping(hosts="red[01-03]")
            pprint(result)

        except Exception as e:
            Console.error("Make sure you have the following in your ~/.ssh/config")
            print(config_hosts)
            Console.error(
                "Make sure you have the ssh remote login enabled")
            print(e)
            Console.error("Your computer is not properly set up to do the test")
            sys.exit()

    def test_ssh_config(self):
        HEADING()

        results = CommonHost.ssh(hosts="red[01-03]", command="uname")
        pprint(results)

        for result in results:
            assert result.stdout.strip().lower() == sys.platform

    def test_ssh_keygen(self):
        HEADING()

        hosts = Parameter.expand("red[01-03]")
        for host in hosts:
            banner(host)
            result = CommonHost.ssh_keygen(
                hosts=host,
                filename=f"~/.ssh/id_rsa_{host}",
                dryrun=False)
            # time.sleep(1)
            banner("result", c="-")
            pprint(result)

            # assert len(result[0]) > 1

    def test_gather_keys(self):
        HEADING()
        hosts = Parameter.expand("red[01-03]")
        result = CommonHost.gather_keys(hosts=hosts)

        pprint(result)

        assert len(result) == len(hosts)

    def test_clean(self):
        HEADING()

        hosts = Parameter.expand("red[01-03],tmp")

        for host in hosts:
            filename = path_expand(f"~/.ssh/id_rsa_{host}")
            print(f"rm {filename} {filename}.pub ")
            try:
                os.remove(filename)
                os.remove(f"{filename}.pub")
            except Exception as e:  # noqa: F841
                pass
