import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    "plot_templates", "../common/plot_templates.py"
)
ptl = importlib.util.module_from_spec(spec)
sys.modules["plot_templates"] = ptl
spec.loader.exec_module(ptl)


def call(jobs):
    """entry point for plotting"""
    # storage format
    # assets/images/plots/hash.png
    # assets/images/plots/hash.json

    ptl.dispatch_plot(ptl.gko_break_down_over_runs, (jobs, "p"))
    ptl.dispatch_plot(ptl.simple_break_down, (jobs, "p"))
    ptl.dispatch_plot(ptl.gko_break_down_over_x, (jobs, "p", "solver"))
    ptl.dispatch_plot(ptl.gko_break_down_over_x, (jobs, "p", "nSubDomains"))
    ptl.dispatch_plot(ptl.time_over_cells, (jobs, "p"))
