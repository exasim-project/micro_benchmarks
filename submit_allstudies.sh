#!/bin/bash
#SBATCH --job-name=exasim_study
#SBATCH --time=12:00:00
#SBATCH --ntasks=76
#SBATCH --partition=cpuonly
#SBATCH --account=hk-project-exasim 
#SBATCH --mem=239400mb
#SBATCH --exclusive
#SBATCH --output=generate_%j.log

# --- Check working directory ---
echo "[INFO] Current directory: $(pwd)"

if [ ! -f .generation_complete ]; then
    echo "[RUN] Starting generation"
    obr run -o fetchCase || { echo "[ERROR] fetchCase failed"; exit 1; }
    obr run -o blockMesh -t 3 || { echo "[ERROR] blockMesh failed"; exit 1; }
    obr run -o decomposePar -t 3 || { echo "[ERROR] decomposePar failed"; exit 1; }
    obr run -o fvSolution || { echo "[ERROR] fvSolution 1 failed"; exit 1; }
    touch .generation_complete
    echo "[SUCCESS] All generation steps completed"
else
    echo "[SKIP] .generation_complete found; skipping generation step."
fi

echo "[DONE] Generation complete"
