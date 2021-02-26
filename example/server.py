from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import oyaml as yaml

"""
pip install fastapi
pip install uvicorn
wget --recursive --no-parent http://example.com/configs/.vim/

uvicorn server:app --reload
"""

data = {}

app = FastAPI()


def load(filename=None):
    global data
    filename = filename or "~/.cloudmesh/inventory.yaml"
    content = readfile(filename)
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

class Host(BaseModel):
        name: str
        cluster: str
        label: str
        status: str
        service: Optional[str] =None
        os: Optional[str] =None
        ip_public: Optional[str] =None
        ip_private: Optional[str] =None
        project: Optional[str] =None
        owners: Optional[list] =None
        comment: Optional[str] =None
        description: Optional[str] =None
        metadata: Optional[dict] =None

@app.get("/")
def read_root():
    return data


@app.get("/hosts/{name}")
def read_host(name: str):
    return data[name]


@app.put("/hosts/{name}")
def update_host(name: str, host: Host):
    save()
    return {"name": host.name, "name": name}
