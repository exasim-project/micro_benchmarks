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
#import numpy as np
import os
#import shutil
import subprocess


#-------------------------------------------------main--------------------------------------------------------#
def call(jobs, kwargs={}):
    python_commands=["plot_residuals.py","plot_Ubar.py","plot_Urms_max.py","plot_fieldMinMax.py","plot_wSS_top.py","plot_wallUnits.py"]
    pvpython_commands=["state_pressure_flowside.py","state_pressure_flownormal.py"]
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

        os.chdir(job.path+"/case")

        for element in python_commands:
            # Run the command and capture output
            try:
                result = subprocess.run(["python3",job.path+"/../../assets/scripts/python-files/"+element], check=True, capture_output=True, text=True)
                print("Output:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error:", e.stderr)
        for element in pvpython_commands:
            # Run the command and capture output
            try:
                result = subprocess.run(["pvpython","--force-offscreen-rendering",job.path+"/../../assets/scripts/"+element], check=True, capture_output=True, text=True)
                print("Output:", result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error:", e.stderr)
        os.chdir(base_dir)