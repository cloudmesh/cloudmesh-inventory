###############################################################
# pytest -v --capture=no  tests/test_inventory..py::Test_inventory  .test_001
# pytest -v --capture=no  tests/test_inventory  .py
# pytest -v tests/test_inventory  .py
###############################################################

from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.host.host import Host
import pytest


@pytest.mark.incremental
class Test_host:

    def setup(self):
        self.h = Host()

    def test_host(self):
        HEADING()
