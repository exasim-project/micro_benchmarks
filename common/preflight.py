import os
from  pprint import pprint 
from subprocess import check_output

def version_checker(d, cmd_str):
    cmd = cmd_str.split()
    d[cmd_str] = check_output(cmd, text=True)

def main():
    environ = dict(os.environ)
    version_checker(environ, "mpirun --version")
    version_checker(environ, "which mpirun")
    version_checker(environ, "lscpu")
    pprint(environ)


if __name__ == "__main__":
    main()
