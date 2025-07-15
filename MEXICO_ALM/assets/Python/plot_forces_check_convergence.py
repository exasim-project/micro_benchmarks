#!/usr/bin/python3

"""
Author: Angelo Busse
Date: 02.02.2024
Requirements: numpy, matplotlib, os
Description: This script plots torque and thrust over time from a SOWFA Actuator Line simulation. 
             It also calculates these values averaged over the last rotation 
             and checks the first convergence criterion from the MEXICO report. 
"""

#-----------------------------------------------libaries------------------------------------------------------#

import matplotlib.pyplot as plt
import numpy as np
import os

#----------------------------------------------userInputs-----------------------------------------------------#

# Option to plot the rolling mean and adjust the window size for it's calculation
plot_rolling_mean = False
window_size = 360 

# Input experimental values as references
exp_thrust_input = 1663
exp_torque_input = 317

show_plots = False

save_plots = True
                      
#-------------------------------------------------main--------------------------------------------------------#
def plot_forces_check_convergence(casePath,outDir):
    # Specify the base path to the directories containing data
    base_path = casePath+'/postProcessing/turbineOutput/' 
    # List all subdirectories (linked to time)
    time_directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]

    # Get the number of columns in the data (default 4 for SOWFA)
    num_columns = 4

    # Initialize empty arrays to store data
    all_data_force_thrust = np.empty((0, num_columns))
    all_data_moment_torque = np.empty((0, num_columns))

    # Iterate over time directories
    for time_dir in time_directories:
        # Construct paths to thrust and torque files
        path_to_thrust = os.path.join(base_path, time_dir, 'rotorAxialForce')
        path_to_torque = os.path.join(base_path, time_dir, 'rotorTorque')

        # Read cfd data for each time directory
        data_force_thrust = np.loadtxt(path_to_thrust)
        data_moment_torque = np.loadtxt(path_to_torque)

        # Concatenate the data to the arrays
        all_data_force_thrust = np.concatenate((all_data_force_thrust, data_force_thrust))
        all_data_moment_torque = np.concatenate((all_data_moment_torque, data_moment_torque))

    # Extract columns
    thrust_cfd = all_data_force_thrust [:,3]
    torque_cfd = all_data_moment_torque[:,3]
    time_cfd = all_data_moment_torque[:,1]
    last_time = time_cfd[-1]

    # Calculate the rolling mean
    if plot_rolling_mean:
        thrust_cfd_mean = np.convolve(thrust_cfd, np.ones(window_size)/window_size, mode='valid')
        torque_cfd_mean = np.convolve(torque_cfd, np.ones(window_size)/window_size, mode='valid')
        time_cfd_mean = np.convolve(time_cfd, np.ones(window_size)/window_size, mode='valid')

    # Exp data
    thrust_exp = np.full(len(time_cfd), exp_thrust_input)
    torque_exp = np.full(len(time_cfd), exp_torque_input)

    # Create a figure
    fig, axs = plt.subplots(2, 1, figsize=(8, 10))

    # Plot the experimental data
    axs[0].plot( time_cfd, thrust_exp, c='green', label='exp', linewidth=2)
    axs[1].plot( time_cfd, torque_exp, c='green', label='exp', linewidth=2)

    # Plot the cfd data
    axs[0].plot( time_cfd, thrust_cfd, c='orange', label='cfd', linewidth=1)
    axs[1].plot( time_cfd, torque_cfd, c='orange', label='cfd', linewidth=1)

    if plot_rolling_mean:
        axs[0].plot( time_cfd_mean, thrust_cfd_mean, c='blue', label='cfd_mean', linewidth=2)
        axs[1].plot( time_cfd_mean, torque_cfd_mean, c='blue', label='cfd_mean', linewidth=2)

    # Set labels and titles for each subplot
    axs[0].set_xlabel('time[s]', fontsize=20)
    axs[0].set_ylabel('Thrust[N]', fontsize=20)
    axs[0].set_title('Thrust vs. time, ALM', fontsize=20)
    axs[0].set_xlim(4.2336, last_time)
    #axs[0].set_ylim(ymin=1600, ymax=2000)
    axs[0].grid(True)
    axs[0].tick_params(labelsize=20)

    axs[1].set_xlabel('time[s]', fontsize=20)
    axs[1].set_ylabel('Torque[Nm]', fontsize=20)
    axs[1].set_title('Torque vs. time, ALM', fontsize=20)
    axs[1].set_xlim(4.2336, last_time)
    #axs[1].set_ylim(ymin=300, ymax=380)
    axs[1].grid(True)
    axs[1].tick_params(labelsize=20)

    # Add legend
    axs[0].legend(loc='upper right')
    axs[1].legend(loc='upper right')

    # Adjust the layout
    plt.tight_layout()

    # Save the figure
    if save_plots:
        plt.savefig(outDir+'/forces_ALM.png', dpi=300, bbox_inches='tight')

    # Show the figure
    if show_plots:
        plt.show()

    # Calculate first MEXICO convergence criterium
    revolution_time = 0.14114326
    time_interval = time_cfd[-1] - time_cfd[-2]     # assume constant time interval in last rotation
    points_per_revolution = int(revolution_time / time_interval)

    # Extract values from last roation 
    last_revolution_thrust = thrust_cfd[-points_per_revolution:]
    last_revolution_torque = torque_cfd[-points_per_revolution:]

    # Calculate mean in last revolution and difference to experimental values
    thrust_last_revolution_mean = np.mean(last_revolution_thrust)
    torque_last_revolution_mean = np.mean(last_revolution_torque)
    diff_thrust = 100 * (thrust_last_revolution_mean - exp_thrust_input) / exp_thrust_input
    diff_torque = 100 * (torque_last_revolution_mean - exp_torque_input) / exp_torque_input

    # Calculate min and max values within the last revolution
    thrust_final_var = np.array([np.min(last_revolution_thrust), np.max(last_revolution_thrust)])
    torque_final_var = np.array([np.min(last_revolution_torque), np.max(last_revolution_torque)])

    # Calculate variation in last revolution in percent
    thrust_variation_percent = 100 * abs((thrust_final_var[1] - thrust_final_var[0]) / thrust_final_var[0])
    torque_variation_percent = 100 * abs((torque_final_var[1] - torque_final_var[0]) / torque_final_var[0])

    print(f"Thrust variation in last rotation (target < 0.25%): {thrust_variation_percent:.4f}%")
    print(f"Torque variation in last rotation (target < 0.50%): {torque_variation_percent:.4f}%")

    print(f"Thrust mean in last rotation (target {exp_thrust_input:.4f} N): {thrust_last_revolution_mean:.4f} N")
    print(f"Torque mean in last rotation (target {exp_torque_input:.4f} Nm): {torque_last_revolution_mean:.4f} Nm")

    print(f"Thrust deviation to experiment: {diff_thrust:.4f}%")
    print(f"Torque deviation to experiment: {diff_torque:.4f}%")
