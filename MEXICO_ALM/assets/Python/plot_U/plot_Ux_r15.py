#!/usr/bin/python3

"""
Author: Angelo Busse
Date: 02.02.2024
Requirements: numpy, matplotlib, os
Description: This script plot the three velocity components for the axial traverses of the MEXICO case with experimental data.
"""

#-----------------------------------------------libaries------------------------------------------------------#

import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MultipleLocator

#----------------------------------------------userInputs-----------------------------------------------------#

# colors for plotting
colors = ['orange', 'darkviolet', 'deepskyblue']

show_plots = False

save_plots = True
                      
#-------------------------------------------------main--------------------------------------------------------#

# Function to load CFD data from a given folder
def load_cfd_data(folder):
    file_path = os.path.join('', folder, 'r_1_5_U.xy')
    U_data = np.loadtxt(file_path)

    data_x = U_data[:,0]
    data_Ux = U_data[:,3]
    data_Uy = U_data[:,4]
    data_Uz = U_data[:,5]

    return data_x, data_Ux, data_Uy, data_Uz

def plot_Ux_r15(outDir,expData):
    folders=[outDir]
    # load EXP data as .dat file
    file_path2 = expData+'/AxOut_NewMexico.dat'
    exp_U_data = np.genfromtxt(file_path2, dtype=float, missing_values='NA', filling_values=np.nan)
    exp_data_x = exp_U_data[:,0]
    exp_data_Ux = exp_U_data[:,4]
    exp_data_Uy = exp_U_data[:,5]
    exp_data_Uz = exp_U_data[:,6]

    # Create a figure
    fig, axs = plt.subplots(3, 1, figsize=(8, 12))

    # Iterate over the folders and plot the CFD data
    for idx, folder in enumerate(folders):
        data_x_0, data_Ux, data_Uy, data_Uz = load_cfd_data(folder)

        axs[0].plot(data_x_0, data_Ux, label='cfd', linewidth=2, color=colors[idx])
        axs[1].plot(data_x_0, data_Uy, label='cfd', linewidth=2, color=colors[idx])
        axs[2].plot(data_x_0, data_Uz, label='cfd', linewidth=2, color=colors[idx])

    # Plot the experimental data
    axs[0].scatter(exp_data_x, exp_data_Ux, s=3, c='maroon', label='exp')
    axs[1].scatter(exp_data_x, exp_data_Uy, s=3, c='maroon', label='exp')
    axs[2].scatter(exp_data_x, exp_data_Uz, s=3, c='maroon', label='exp')

    # Set labels and titles for each subplot
    axs[0].set_xlabel('x[m]', fontsize=20)
    axs[0].set_ylabel('Ux[m/s]', fontsize=20)
    axs[0].set_title('Ux vs. x, r=1.5', fontsize=20)
    axs[0].tick_params(labelsize=20)
    axs[0].grid(True)
    axs[0].xaxis.set_minor_locator(MultipleLocator(0.2))
    axs[0].yaxis.set_minor_locator(MultipleLocator(1))
    axs[0].set_xlim([-4.5, 6])
    axs[0].set_ylim([2, 16])

    axs[1].set_xlabel('x[m]', fontsize=20)
    axs[1].set_ylabel('Uy[m/s]', fontsize=20)
    axs[1].set_title('Uy vs. x, r=1.5', fontsize=20)
    axs[1].tick_params(labelsize=20)
    axs[1].grid(True)
    axs[1].xaxis.set_minor_locator(MultipleLocator(0.2))
    axs[1].yaxis.set_minor_locator(MultipleLocator(0.25))
    axs[1].set_xlim([-4.5, 6])
    axs[1].set_ylim([-1, 3])

    axs[2].set_xlabel('x[m]', fontsize=20)
    axs[2].set_ylabel('Uz[m/s]', fontsize=20)
    axs[2].set_title('Uz vs. x, r=1.5', fontsize=20)
    axs[2].tick_params(labelsize=20)
    axs[2].grid(True)
    axs[2].xaxis.set_minor_locator(MultipleLocator(0.2))
    axs[2].yaxis.set_minor_locator(MultipleLocator(0.25))
    axs[2].set_xlim([-4.5, 6])
    axs[2].set_ylim([-2, 2])

    # Add legend
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')
    axs[2].legend(loc='upper right')

    # Adjust the layout
    plt.tight_layout()

    # Save the figure
    if save_plots:
        plt.savefig(outDir+'/U_x_r15.png', dpi=300, bbox_inches='tight')

    # Show the figure
    if show_plots:
        plt.show()