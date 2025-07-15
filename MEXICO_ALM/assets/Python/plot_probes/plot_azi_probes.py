#!/usr/bin/python3

"""
Author: Angelo Busse
Date: 02.02.2024
Requirements: numpy, matplotlib, os, re
Description: This script plots the three velocity components for the probes (azimuth traverses) of the MEXICO case with experimental data.
"""

#-----------------------------------------------libaries------------------------------------------------------#

import numpy as np
import matplotlib.pyplot as plt
import os
import re
from matplotlib.ticker import MultipleLocator

#----------------------------------------------userInputs-----------------------------------------------------#

colors = ['deepskyblue', 'orange', 'darkviolet']

time_steps_in_last_rotation = 360

show_plots = False

save_plots = True
                      
#-------------------------------------------------main--------------------------------------------------------#

# Function to load CFD data from a given  folder
def load_cfd_data(folder):
    file_path = folder

    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse the data, skipping lines starting with '#'
    time = []
    Y1 = []
    Y2 = []
    Y3 = []
    
    for line in lines:
        if not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 2:
                time.append(float(parts[0]))
                match = re.search(r'\((.*)\)', line)
                if match:
                    values_list = [float(val) for val in match.group(1).split()]
                    Y1.append(values_list[0])
                    Y2.append(values_list[1])
                    Y3.append(values_list[2])
    
    # Convert lists to NumPy arrays & extract values from last roation 
    revolution_time = 0.14114326
    data_time = np.array(time)
    time_interval = data_time[-1] - data_time[-2]                   # assume constant time interval in last rotation
    points_per_revolution = int(revolution_time / time_interval)

    data_time = data_time[-points_per_revolution:] 
    
    data_Ux = np.array(Y1)[-points_per_revolution:]
    data_Uy = np.array(Y2)[-points_per_revolution:]
    data_Uz = np.array(Y3)[-points_per_revolution:]
    data_phi = np.arange(1, len(data_Ux) + 1)

    return data_phi, data_Ux, data_Uy, data_Uz

def plot_azi_probes(casePath,outDir,expData,probeName,expName,rPosLabel):
    base_path=casePath+'/postProcessing/'+probeName
    # List all subdirectories (linked to time) and latest time step
    time_directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    latest_time_directory = time_directories[-1]
    folders=[base_path+'/'+str(latest_time_directory)+'/U']
    # Create a figure
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))    
        
    # Iterate over the  folders and plot the CFD data
    for idx, folder in enumerate(folders):
        data_phi, data_Ux, data_Uy, data_Uz = load_cfd_data(folder)

        axs[0].plot(data_phi, data_Ux, label='cfd', linewidth=2, color=colors[idx])
        axs[1].plot(data_phi, data_Uy, label='cfd', linewidth=2, color=colors[idx])
        axs[2].plot(data_phi, data_Uz, label='cfd', linewidth=2, color=colors[idx])
        
    # load EXP data as .dat file
    file_path2 = expData+'/'+expName
    exp_U_data = np.genfromtxt(file_path2, dtype=float, missing_values='NA', filling_values=np.nan)
    exp_data_phi = exp_U_data[:,0]
    exp_data_Ux = exp_U_data[:,4]
    exp_data_Uy = exp_U_data[:,5]
    exp_data_Uz = exp_U_data[:,6]

    # Plot the experimental data
    axs[0].scatter(exp_data_phi, exp_data_Ux, s=3, c='maroon', label='exp')
    axs[1].scatter(exp_data_phi, exp_data_Uy, s=3, c='maroon', label='exp')
    axs[2].scatter(exp_data_phi, exp_data_Uz, s=3, c='maroon', label='exp')

    # Set labels and titles for each subplot
    axs[0].set_xlabel('phi[°]', fontsize=20)
    axs[0].set_ylabel('Ux[m/s]', fontsize=20)
    axs[0].set_title('Ux vs. phi, '+rPosLabel, fontsize=20)
    axs[0].grid(True)
    axs[0].tick_params(labelsize=20)
    axs[0].xaxis.set_minor_locator(MultipleLocator(5))
    axs[0].yaxis.set_minor_locator(MultipleLocator(0.5))
    axs[0].set_xlim([0, 120])
    #axs[0].set_ylim([10, 16])

    axs[1].set_xlabel('phi[°]', fontsize=20)
    axs[1].set_ylabel('Uy[m/s]', fontsize=20)
    axs[1].set_title('Uy vs. phi, '+rPosLabel, fontsize=20)
    axs[1].grid(True)
    axs[1].tick_params(labelsize=20)
    axs[1].xaxis.set_minor_locator(MultipleLocator(5))
    axs[1].yaxis.set_minor_locator(MultipleLocator(0.05))
    axs[1].set_xlim([0, 120])
    #axs[1].set_ylim([0, 1.20])

    axs[2].set_xlabel('phi[°]', fontsize=20)
    axs[2].set_ylabel('Uz[m/s]', fontsize=20)
    axs[2].set_title('Uz vs. phi, '+rPosLabel, fontsize=20)
    axs[2].grid(True)
    axs[2].tick_params(labelsize=20)
    axs[2].xaxis.set_minor_locator(MultipleLocator(5))
    axs[2].yaxis.set_minor_locator(MultipleLocator(0.1))
    axs[2].set_xlim([0, 120])
    #axs[2].set_ylim([-0.5, 1])

    # Add legend
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')
    axs[2].legend(loc='upper right')

    # Adjust the layout
    plt.tight_layout()

    # Save the figure
    if save_plots:
        plt.savefig(outDir+'/'+probeName+'.png', dpi=300, bbox_inches='tight')
    plt.close()
    # Show the figure
    if show_plots:
        plt.show()