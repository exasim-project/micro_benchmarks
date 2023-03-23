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
        {% set walltime = operations | calc_walltime(parallel) %}
        {% if walltime %}
#SBATCH -t {{ walltime|format_timedelta }}
        {% endif %}
        {% if job_output %}
#SBATCH --output={{ job_output }}
#SBATCH --error={{ job_output }}
        {% endif %}
    {% endblock preamble %}
#SBATCH --gpus-per-node={{ gpus_per_node }}
#SBATCH --tasks-per-node={{ tasks_per_node }}
#SBATCH --account=haicore-project-scc
{% endblock header %}
