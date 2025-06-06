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

def load_ref(path):
    DNS = {}
    DNS['mean'] = np.genfromtxt(f'{path}/spectralDNS/mean.dat')
    DNS['var'] = np.genfromtxt(f'{path}/spectralDNS/var.dat')

    # extract some data from the DNS case array, so that they have the same
    # structure as the OpenFOAM case
    ny = DNS['mean'][:,0].size
    DNS['U'] = DNS['mean'][1:(ny-3)//2+1,0:2]
    DNS["u'"] = DNS['var'][1:(ny-3)//2+1,0:2];    DNS["u'"][:,1] = DNS["u'"][:,1]**0.5
    DNS["v'"] = DNS['var'][1:(ny-3)//2+1,[0,2]];  DNS["v'"][:,1] = DNS["v'"][:,1]**0.5
    DNS["w'"] = DNS['var'][1:(ny-3)//2+1,[0,3]];  DNS["w'"][:,1] = DNS["w'"][:,1]**0.5

    # some bulk statistics of the spectral DNS case
    DNS['delra_ni'] = 0.00275052
    DNS['utau'] = 0.05275557

    refdir="ISTMopenFOAMrun"
    #refdir="UCFDopenFOAMrun"

    # import data of ISTM OpenFOAM run
    OpenFOAM = {}
    OpenFOAM['U']      = np.loadtxt(f'{path}/{refdir}/Uf.xy', dtype=np.float64)
    OpenFOAM["u'"] = np.loadtxt(f'{path}/{refdir}/u.xy', dtype=np.float64)
    OpenFOAM["v'"] = np.loadtxt(f'{path}/{refdir}/v.xy', dtype=np.float64)
    OpenFOAM["w'"] = np.loadtxt(f'{path}/{refdir}/w.xy', dtype=np.float64)
    # some bulk statistics of the ISTM OpenFOAM run
    PGOF = np.genfromtxt(f'{path}/ISTMopenFOAMrun/pGrad.txt')
    MPGOP = np.average(PGOF)
    OpenFOAM['utau'] = np.sqrt(MPGOP)
    OpenFOAM['nu'] = 1.45105e-04
    OpenFOAM['delta_ni'] = OpenFOAM['nu']/OpenFOAM['utau']
    return DNS,OpenFOAM

def load_data_sample(path):
    files = glob.glob(f'{path}/case/postProcessing/sampleDict_line/*/lineR_pMean_pPrime2Mean_UMean_UPrime2Mean.xy')
    files.sort(key=lambda x: x.split('/')[-2])  # Sort by time directory

    # Get column names from the last file (assumes consistent format)
    #headers = pd.read_csv(files[-1], sep='\t', skiprows=4, nrows=0).columns.str.strip('# ')
    headers = ["y","pMean","pPrime2Mean","Ux","Uy","Uz","uu","uv","uw","vv","vw","ww"]

    # Load data into DataFrame
    df = pd.concat(
        (pd.read_csv(filename, sep='\t', comment='#', header=None, names=headers) for filename in files),
        ignore_index=True
    )

    Retau=363.6

    # Convert 'areaAverage(U)' column from string to NumPy array
    #df['areaAverage(U)'] = df['areaAverage(U)'].str.replace(' ', ',').apply(ast.literal_eval).apply(np.asarray)

    df['yplus'] = df['y'].apply(lambda u: u*Retau)
    df['pRMS'] = df['pPrime2Mean'].apply(lambda u: np.sqrt(u))
    df['Urms'] = df['uu'].apply(lambda u: np.sqrt(np.abs(u)))
    df['Vrms'] = df['vv'].apply(lambda u: np.sqrt(np.abs(u)))
    df['Wrms'] = df['ww'].apply(lambda u: np.sqrt(np.abs(u)))

    return df

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

def get_params2(data):
    ranks_per_gpu = None
    last_np = None
    preconditioner = None
    latest_time = data.get("state", {}).get("latestTime")

    for entry in reversed(data.get('history', [])):
        cmd = entry.get('cmd', '')

        if last_np is None and 'mpirun' in cmd:
            match = re.search(r'-np\s+(\d+)', cmd)
            if match:
                last_np = int(match.group(1))

        if (ranks_per_gpu is None or preconditioner is None) and cmd == 'set_key_value_pairs':
            args_str = entry.get('args', '')
            try:
                args_dict = ast.literal_eval(args_str)
                dictionary = args_dict.get('dictionary', {})
                ranks_per_gpu = ranks_per_gpu or dictionary.get('ranksPerGPU')
                preconditioner = preconditioner or dictionary.get('preconditioner')
            except Exception as e:
                print(f"Error parsing dictionary: {e}")

        if last_np is not None and ranks_per_gpu is not None and preconditioner is not None:
            break

    return ranks_per_gpu, last_np, preconditioner, latest_time

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
    DNS,OpenFOAM = load_ref("./benchmarkData")
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

        rpg,npp,preconditioner, latest_time = get_params2(job.doc)
        df=load_data_sample(job.path)
        df['rpg']=rpg
        df['np']=npp
        df['precon']=preconditioner
        if latest_time < 780:
            df['converged']=False
        else:
            df['converged']=True
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
    with open("sample_line.json", "w") as f:
        json.dump(json_dict, f, indent=4)
    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Ux"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Ux"], label=lblstr,alpha=alpha)
        #else:    
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    ax.plot(363.6*DNS['U'][2:,0], DNS['U'][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.plot(363.6*OpenFOAM['U'][:, 0], OpenFOAM['U'][:,1], 'k',linewidth=0.5,markerfacecolor="None", label='OpenFOAM ISTM')
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{U}/U_b$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_Ux_all.png', dpi=450, facecolor='w', edgecolor='w', 
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

###################################################################

    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Urms"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Urms"], label=lblstr,alpha=alpha)
        #else:
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    ax.plot(363.6*DNS["u'"][2:,0], DNS["u'"][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.plot(363.6*OpenFOAM["u'"][:, 0], OpenFOAM["u'"][:,1], 'k',linewidth=0.5,markerfacecolor="None", label='OpenFOAM ISTM')
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{U}_{RMS}/U_b$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_Urms_all.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

###################################################################

    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Vrms"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Vrms"], label=lblstr,alpha=alpha)
        #else:
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    ax.plot(363.6*DNS["v'"][2:,0], DNS["v'"][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.plot(363.6*OpenFOAM["v'"][:, 0], OpenFOAM["v'"][:,1], 'k',linewidth=0.5,markerfacecolor="None", label='OpenFOAM ISTM')
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{V}_{RMS}/U_b$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_Vrms_all.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

###################################################################

    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Wrms"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["Wrms"], label=lblstr,alpha=alpha)
        #else:
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    ax.plot(363.6*DNS["w'"][2:,0], DNS["w'"][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.plot(363.6*OpenFOAM["w'"][:, 0], OpenFOAM["w'"][:,1], 'k',linewidth=0.5,markerfacecolor="None", label='OpenFOAM ISTM')
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{W}_{RMS}/U_b$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_Wrms_all.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

###################################################################

    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["pMean"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["pMean"], label=lblstr,alpha=alpha)
        #else:
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    #ax.plot(363.6*DNS["w'"][2:,0], DNS["w'"][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{p}$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_pMean_all.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)

###################################################################

    fig, ax = plt.subplots(figsize=(8, 5))
    alphas = np.linspace(0.3, 1, len(data_all_jobs))
    for key,alpha in zip(data_all_jobs.keys(),alphas):
        rpg=data_all_jobs[key]['rpg'].values[0]
        npp=data_all_jobs[key]['np'].values[0]
        if data_all_jobs[key]['precon'].values[0] == "BJ":
            solvstr="GKOCG"
        elif data_all_jobs[key]['precon'].values[0] == "none":
            solvstr="GAMG"
        elif data_all_jobs[key]['precon'].values[0] == "FDIC":
            solvstr="PCG"
        else:
            solvstr="GKOMG"
        #lblstr="RPG:%i, NP: %i" % (rpg,npp)
        lblstr="%s -np %i -rpg %i" % (solvstr,npp,rpg)
        if 4*rpg==npp:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["pRMS"],linestyle=':', label=lblstr,alpha=alpha)
        else:
            ax.plot(data_all_jobs[key]["yplus"], data_all_jobs[key]["pRMS"], label=lblstr,alpha=alpha)
        #else:
         #   ax.plot(data_all_jobs[key]["Time"], data_all_jobs[key]["Urms"],linestyle=':', color='#1C81AC',label=lblstr,alpha=alpha)
    #ax.plot(363.6*DNS["w'"][2:,0], DNS["w'"][2:,1], 'k.',markerfacecolor="None", label='Spectral DNS', zorder=1)
    ax.legend(ncols=3,fontsize=7)
    ax.set_title("PeriodicChannel (4GPU per node)")
    ax.set_ylabel(r"$\overline{p}'$ [-]")
    ax.set_xlabel(r"$y^+$ [-]")
    ax.set_xscale('log')
    #ax.set_ylim((0,0.3))
    plt.savefig('fig_sample_pRMS_all.png', dpi=450, facecolor='w', edgecolor='w',
            orientation='portrait', bbox_inches='tight', pad_inches=0.1)
