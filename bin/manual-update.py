# !/usr/bin/env python

from cloudmesh.common.Shell import Shell
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
import textwrap

try:
    manual = 0
    man = Shell.run("cms help inventory")

    # remove timer
    man = man.split("\nTimer: ")[0]

    readme = readfile("README.md")

    parts = readme.split("<!-- MANUAL -->")

    content = []

    content.append(parts[0].strip())
    content.append("")
    content.append("<!-- MANUAL -->")
    content.append("```")
    content.append(textwrap.dedent("\n".join(man.splitlines()[7:])))
    content.append("```")
    content.append("<!-- MANUAL -->")
    try:
        content.append(parts[2])
    except:
        pass

    print ("\n".join(content))
except Exception as e:
    print (e)


