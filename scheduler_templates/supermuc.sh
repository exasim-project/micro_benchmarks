{% extends "base_script.sh" %}
{% block header %}
    {% block preamble %}
#!/bin/bash
#SBATCH --job-name="{{ id }}"
        {% set memory_requested = operations | calc_memory(parallel)  %}
        {% if memory_requested %}
#SBATCH --mem={{ memory_requested|format_memory }}
        {% endif %}
{% if partition %}
#SBATCH --partition={{ partition }}
{% endif %}
{% if walltime %}
#SBATCH -t {{ walltime }}
{% endif %}
        {% if job_output %}
#SBATCH --output={{ job_output }}
#SBATCH --error={{ job_output }}
{% endif %}
    {% endblock preamble %}

{% if gpus_per_node %}
#SBATCH --gpus-per-node={{ gpus_per_node }}
{% endif %}

#SBATCH --ntasks={{ operations|calc_tasks('np', parallel, force) }}
{% if nodes %}
{% set nnodes = nodes | int %}
#SBATCH --tasks-per-node={{ operations|calc_tasks('np', parallel, force) // nnodes }}
{% else %}
#SBATCH --tasks-per-node={{ tasks_per_node }}
{% endif %}

{% if account %}
#SBATCH --account={{ account }}
{% endif %}

module load cmake
module load ninja
module load gcc
module load gdb
module load flex
module load git
module load intel-toolkit
source $HOME/OpenFOAM/openfoam/etc/bashrc
export ONEAPI_DEVICE_SELECTOR=level_zero:0
export GIT_PYTHON_REFRESH=w

{% endblock header %}
