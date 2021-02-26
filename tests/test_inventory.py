###############################################################
# pytest -v --capture=no  tests/test_inventory.py::Test_inventory.test_001
# pytest -v --capture=no  tests/test_inventory.py
# pytest -v tests/test_inventory.py
###############################################################

import pytest
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import banner
from cloudmesh.inventory.inventory import Inventory


@pytest.mark.incremental
class Test_inventory:

    def setup(self):
        self.i = Inventory('~/.cloudmesh/test.yaml')
        self.i.info()

    def test_add(self):
        HEADING(txt="cms inventory add")
        cluster = "test_cluster"
        label = "test{j}"
        host = "red00{j}"
        ip = "10.1.1.{j}"
        dns = "8.8.8.8"

        # Adding one by one
        for j in range(1, 4):
            self.i.add(host=host.format(j=j), cluster=cluster, dns=dns, label=label.format(j=j), ip=ip.format(j=j),)

        for j in range(1, 4):
            host_name = host.format(j=j)
            assert self.i.has_host(host_name)
            entry = self.i.data[host_name]
            assert entry['cluster'] == cluster
            assert entry['ip'] == ip.format(j=j)
            assert entry['label'] == label.format(j=j)
            assert entry['dns'] == dns

        # Multi add
        self.i.add(host=host.format(j='[4-7]'), cluster=cluster, ip=ip.format(j='[4-7]'))

        for j in range(4, 8):
            host_name = host.format(j=j)
            assert self.i.has_host(host_name)
            entry = self.i.data[host_name]
            assert entry['cluster'] == cluster
            assert entry['ip'] == ip.format(j=j)

        self.i.save()

    def test_list(self):
        HEADING(txt="cms inventory list")

        # for output in ['dict', 'yaml', 'csv', 'table']: # bug in 'csv' print in cloudmesh-common
        for output in ['dict', 'yaml', 'table']:
            banner(output)
            print(self.i.list(format=output))

        t = str(self.i.list('table'))

        for order in self.i.order:
            assert order in t

    def test_set(self):
        HEADING()

        self.i.set("red002", "service", "worker")
        assert self.i.get("red002", "service") == "worker"
        self.i.save()

    def test_find(self):
        HEADING()
        assert len(self.i.find(host="red002")) > 0


"""
# We need nostest for this

cms inventory list
cms inventory help
cms help inventory
cms inventory list d[1-3]
cms inventory list
cms inventory add d[1-3] --project=openstack
"""
