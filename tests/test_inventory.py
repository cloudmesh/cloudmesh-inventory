###############################################################
# pytest -v --capture=no  tests/test_inventory..py::Test_inventory  .test_001
# pytest -v --capture=no  tests/test_inventory  .py
# pytest -v tests/test_inventory  .py
###############################################################

from pprint import pprint

from cloudmesh.common.Printer import Printer
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.inventory.inventory import Inventory
import pytest


@pytest.mark.incremental
class Test_inventory:

    def setup(self):
        self.i = Inventory()
        banner("Info")
        self.i.info()

    def test_inventory(self):
        HEADING()

        for output in ['dict', 'yaml', 'csv', 'table']:
            banner(output)
            print(self.i.list(format=output))

        banner("changing values")
        self.i.add(host="i1", cluster="india", label="india")
        self.i.add(host="i2", cluster="india", label="gregor")
        self.i.add(host="d[1-4]", cluster="delta", label="delta")

        banner("saving")
        self.i.save()

        for output in ['dict', 'yaml', 'csv', 'table']:
            banner(output)
            print(self.i.list(format=output))

        banner("reading")
        n = Inventory()
        n.read()

        t = n.list('table')
        print(t)

        assert "gregor" in str(t)
        assert "+" in str(t)


"""
# We need nostest for this

cms inventory list
cms inventory help
cms help inventory
cms inventory list d[1-3]
cms inventory list 
cms inventory add d[1-3] --project=openstack
"""
