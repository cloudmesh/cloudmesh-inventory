from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import oyaml as yaml
import os

"""
pip install fastapi
pip install uvicorn
git clone https://github.com/cloudmesh/cloudmesh-inventory
cd cloudmesh-inventory/example/
uvicorn server:app --reload

# http://127.0.0.1:8000/docs 
"""


sample = """
d1:
  cluster: delta
  comment: ''
  host: d1
  ip: ''
  label: delta
  name: ''
  owners: ''
  project: openstack
  service: ''
d2:
  cluster: delta
  comment: ''
  host: d2
  ip: ''
  label: delta
  name: ''
  owners: ''
  project: openstack
  service: ''
"""

data = {}

app = FastAPI()


def load(filename=None):
    global data
    filename = filename or "~/.cloudmesh/inventory.yaml"
    if os.path.exists(filename):
        content = readfile(filename)
    else:
        content = sample
    data = yaml.safe_load(content)


def save(filename=None):
    global data
    filename = filename or "~/.cloudmesh/inventory-tmp.yaml"
    # just so we do not overwrite the original we use tmp
    readfile(filename, data)


@app.on_event("startup")
async def startup_event():
    load()

@app.on_event("shutdown")
async def startup_event():
    save()

# this is not yet used ....

class Host(BaseModel):
        name: str
        cluster: str
        label: str
        status: str
        service: Optional[str] = None
        os: Optional[str] = None
        ip_public: Optional[str] = None
        ip_private: Optional[str] = None
        project: Optional[str] = None
        owners: Optional[list] = None
        comment: Optional[str] = None
        description: Optional[str] = None
        metadata: Optional[dict] = None


@app.get("/")
def read_root():
    return data


@app.get("/hosts/{name}")
def read_host(name: str):
    return data[name]


@app.put("/hosts/{name}")
def update_host(name: str, host: Host):
    # this is not yet properly implemented
    save()
    return {"name": host.name, "name": name}
