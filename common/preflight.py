import os
import re

from  pprint import pprint 
from subprocess import check_output


def is_mpich(env):
    print("Checking if MPI is MPICH")
    assert 'mpich' in env['which mpirun']

def validate_environ(environ):
    pprint(environ)
    machine_alias = find_machine_alias(environ)  
    for requirement in requirements[machine_alias]:
        requirement(environ)

def find_machine_alias(environ):
    hostname = environ["HOSTNAME"]
    for k, vs in machine_alias.items():
        for pattern in vs:
            if re.findall(pattern, hostname):
                return k
    return hostname


def version_checker(d, cmd_str):
    cmd = cmd_str.split()
    d[cmd_str] = check_output(cmd, text=True)

def main():
    environ = dict(os.environ)
    version_checker(environ, "mpirun --version")
    version_checker(environ, "which mpirun")
    version_checker(environ, "lscpu")
    validate_environ(environ)

machine_alias = {
        "guyot": "guyot"
        }

requirements = {
        "guyot": [is_mpich]
        }

if __name__ == "__main__":
    main()
