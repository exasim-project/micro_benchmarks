#!/usr/bin/python3

"""
Author: Angelo Busse
Date: 02.02.2024
Requirements: numpy, os, shutil
Description: This script prepares the velocity samples from cuttingLines for further post processing 
             by coping the axial traveses from the last time step refering to blade 1 pointing upwards
             and calculating the mean velocities for the radial traverses within in last rotation.
"""

#-----------------------------------------------libaries------------------------------------------------------#
#import sys
import numpy as np
import os
import pandas as pd
import glob
import subprocess
import matplotlib.pyplot as plt
import json
import ast, re

#-------------------------------------------------main--------------------------------------------------------#

def load_data_Urms(path):
    files = glob.glob(f'{path}/case/postProcessing/Urms_max/*/volFieldValue.dat')
    print(f'{path}/case/postProcessing/Urms_max/*/volFieldValue.dat')
    files.sort(key=lambda x: x.split('/')[-2])  # Sort by time directory

    # Get column names from the last file (assumes consistent format)
    headers = pd.read_csv(files[-1], sep='\t', skiprows=3, nrows=0).columns.str.strip('# ')

    # Load data into DataFrame
    df = pd.concat(
        (pd.read_csv(filename, sep='\t', comment='#', header=None, names=headers) for filename in files),
        ignore_index=True
    )

    df['Urms'] = df['max(UPrime2Mean)'].apply(lambda u: np.sqrt(u))

    return df

def get_params(data):
    ranks_per_gpu = None
    last_np = None
    for entry in reversed(data['history']):
        cmd = entry.get('cmd', '')

        if last_np is None and 'mpirun' in cmd:
            match = re.search(r'-np\s+(\d+)', cmd)
            if match:
                last_np = int(match.group(1))

        if ranks_per_gpu is None and cmd == 'set_key_value_pairs':
            args_str = entry.get('args', '')
            try:
                args_dict = ast.literal_eval(args_str)
                ranks_per_gpu = args_dict['dictionary'].get('ranksPerGPU')
            except Exception as e:
                print(f"Error parsing ranksPerGPU: {e}")

        # Break early if both values are found
        if last_np is not None and ranks_per_gpu is not None:
            break
    return ranks_per_gpu, last_np

def call(jobs, kwargs={}):
    python_commands=["plot_residuals.py","plot_Ubar.py","plot_Urms_max.py","plot_fieldMinMax.py","plot_wSS_top.py","plot_wallUnits.py"]
    pvpython_commands=["state_pressure_flowside.py","state_pressure_flownormal.py"]
    data_all_jobs = {}
    for job in jobs:
        print("Applying script in ",job.path)
        base_dir=os.getcwd()
        # Specify the base path to the directories containing data
        #base_path = job.path + '/case/postProcessing/cuttingLines'
        #if not os.path.exists(base_path):
        #    continue

        # Specify name for the folder containg all four U files for further postProcessing and plotting
        new_folder_name=job.path + '/plots'

        if not os.path.exists(new_folder_name):
            os.makedirs(new_folder_name)

        rpg,npp = get_params(job.doc)
        df=load_data_Urms(job.path)
        df['rpg']=rpg
        df['np']=npp
        key = job.path.split("/")[-1]
        data_all_jobs[key] = df

        os.chdir(job.path+"/case")

#        for element in python_commands:
#            # Run the command and capture output
#            try:
#                result = subprocess.run(["python3",job.path+"/../../assets/scripts/python-files/"+element], check=True, capture_output=True, text=True)
#                print("Output:", result.stdout)
#            except subprocess.CalledProcessError as e:
#                print("Error:", e.stderr)
#        for element in pvpython_commands:
#            # Run the command and capture output
#            try:
#                result = subprocess.run(["pvpython","--force-offscreen-rendering",job.path+"/../../assets/scripts/"+element], check=True, capture_output=True, text=True)
#                print("Output:", result.stdout)
#            except subprocess.CalledProcessError as e:
#                print("Error:", e.stderr)
        os.chdir(base_dir)

    json_dict = {key: data_all_jobs[key].to_dict(orient="records") for key in data_all_jobs.keys()}
    with open("Urms_max.json", "w") as f:
        json.dump(json_dict, f, indent=4)
    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        lblstr="RPG:%i, NP: %i" % (rpg,npp)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"], color='#1C81AC',label=lblstr,alpha=alpha)
        else:    
            ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"max($U_{RMS}$) [$m/s$]")
    ax.set_xlabel("Time t [s]")
    ax.set_ylim((0, 0.3))
    plt.savefig('fig_Urms_max_global.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

