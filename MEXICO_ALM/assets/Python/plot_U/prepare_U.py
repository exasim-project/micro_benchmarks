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

import numpy as np
import os
import shutil

#----------------------------------------------userInputs-----------------------------------------------------#

# Define how many time folders are within the last rotation
num_last_rotation_outputs = 36

#-------------------------------------------------main--------------------------------------------------------#
def prepare_U(casePath,outDir):
    base_path=casePath+'/postProcessing/cuttingLines'
    new_folder_name=outDir
    # Create new folder
    if not os.path.exists(new_folder_name):
            os.makedirs(new_folder_name)

    # List all subdirectories (linked to time) and latest time step
    time_directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
    latest_time_directory = time_directories[-1]

    # find files in last time for axial traverses 
    path_to_latest_time_r05 = os.path.join(base_path, latest_time_directory, 'r_0_5_U.xy')
    path_to_latest_time_r15 = os.path.join(base_path, latest_time_directory, 'r_1_5_U.xy')

    # Copy the files to the new folder
    shutil.copy(path_to_latest_time_r05, new_folder_name)
    shutil.copy(path_to_latest_time_r15, new_folder_name)

    # Find all time directories that are in the last rotation for averaging
    last_rotation_directories = time_directories[-num_last_rotation_outputs:]

    # Create empty arrays to store the data
    data_r = []
    data_Ux = []
    data_Uy = []
    data_Uz = []

    data_r_minus = []
    data_Ux_minus = []
    data_Uy_minus = []
    data_Uz_minus = []


    # Iterate over time directories for calculating U mean for radial traverses
    for time_dir in last_rotation_directories:

        # Construct paths to both files
        path_to_x03 = os.path.join(base_path, time_dir, 'x_0_3_U.xy')
        path_to_xminus03 = os.path.join(base_path, time_dir, 'x_minus_0_3_U.xy')

        # Load data for x03
        U_data = np.loadtxt(path_to_x03)
        data_r.append(U_data[:, 1])
        data_Ux.append(U_data[:, 3])
        data_Uy.append(U_data[:, 4])
        data_Uz.append(U_data[:, 5])

        # Load data for xminus03
        U_data = np.loadtxt(path_to_xminus03)
        data_r_minus.append(U_data[:, 1])
        data_Ux_minus.append(U_data[:, 3])
        data_Uy_minus.append(U_data[:, 4])
        data_Uz_minus.append(U_data[:, 5])

    # Convert the lists to NumPy arrays
    data_r = np.array(data_r)
    data_Ux = np.array(data_Ux)
    data_Uy = np.array(data_Uy)
    data_Uz = np.array(data_Uz)

    data_r_minus = np.array(data_r_minus)
    data_Ux_minus = np.array(data_Ux_minus)
    data_Uy_minus = np.array(data_Uy_minus)
    data_Uz_minus = np.array(data_Uz_minus)

    # Calculate the mean
    mean_r = np.mean(data_r, axis=0)
    mean_Ux = np.mean(data_Ux, axis=0)
    mean_Uy = np.mean(data_Uy, axis=0)
    mean_Uz = np.mean(data_Uz, axis=0)

    mean_r_minus = np.mean(data_r_minus, axis=0)
    mean_Ux_minus = np.mean(data_Ux_minus, axis=0)
    mean_Uy_minus = np.mean(data_Uy_minus, axis=0)
    mean_Uz_minus = np.mean(data_Uz_minus, axis=0)

    # Stack the arrays together horizontally
    stacked_data_x03 = np.column_stack((mean_r, mean_r, mean_r, mean_Ux, mean_Uy, mean_Uz))
    stacked_data_xminus03 = np.column_stack((mean_r_minus, mean_r_minus, mean_r_minus, mean_Ux_minus, mean_Uy_minus, mean_Uz_minus))

    # Define the output file paths
    output_file_x03 = os.path.join(new_folder_name, 'x_0_3_U.xy')
    output_file_xminus03 = os.path.join(new_folder_name, 'x_minus_0_3_U.xy')

    # Put both mean U files into new folder
    np.savetxt(output_file_x03, stacked_data_x03, delimiter='\t', fmt='%f')
    np.savetxt(output_file_xminus03, stacked_data_xminus03, delimiter='\t', fmt='%f')