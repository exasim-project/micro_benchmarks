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
#SBATCH --partition=compute
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
    {% block tasks %}
#SBATCH --ntasks={{ np_global }}
#SBATCH --time=1-00:00:00
#SBATCH --account=bmbf_2022_EXASIM
    {% endblock tasks %}
ml gnu/11
ml openmpi/3
ml ucfdFOAM/v2212
{% endblock header %}
