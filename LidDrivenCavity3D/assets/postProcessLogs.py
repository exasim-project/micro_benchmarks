import importlib.util
import sys
spec = importlib.util.spec_from_file_location("postProcessLogs", "../common/postProcessLogs.py")
pPL = importlib.util.module_from_spec(spec)
sys.modules["postProcessLogs"] = pPL
spec.loader.exec_module(pPL)

def call(jobs):
    pPL.call(jobs)
