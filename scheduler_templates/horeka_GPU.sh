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

{% if operations|calc_tasks('np', parallel, force) > 8 %}
#SBATCH --gpus-per-node=4
{% else %}
#SBATCH --gpus-per-node={{ operations|calc_tasks('np', parallel, force) // 2 }}
{% endif %}
#SBATCH --ntasks={{ operations|calc_tasks('np', parallel, force) }}

{% set tpn_read = tasks_per_node | int %}

{% if operations|calc_tasks('np', parallel, force) < tpn_read %}
{% set tpn = operations|calc_tasks('np', parallel, force) | int %}
#SBATCH --tasks-per-node={{ tpn }}
{% else %}
#SBATCH --tasks-per-node={{ tasks_per_node }}
{% endif %}


{% if account %}
#SBATCH --account={{ account }}
{% endif %}

export CUDA_VISIBLE_DEVICES="0,1,2,3"
#export CUDA_VISIBLE_DEVICES="0"
module purge
source ~/OBR_ENV/bin/activate
module load devel/cmake/3.26
module load compiler/gnu/13
module load mpi/openmpi/4.1
module load devel/cuda/12.4
export WM_PROJECT_SITE=~/SOWFA
source $HOME/OpenFOAM/OpenFOAM-v2212/etc/bashrc
{% endblock header %}
