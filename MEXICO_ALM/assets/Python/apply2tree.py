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
import sys
import numpy as np
import os
import shutil
sys.path.append("./assets/Python/plot_U")
import prepare_U
import plot_Ux_r15
import plot_Ux_r05
import plot_Ur_x03
import plot_Ur_minusx03
sys.path.append("./assets/Python")
import plot_forces_check_convergence
sys.path.append("./assets/Python/plot_probes")
import plot_azi_probes


#-------------------------------------------------main--------------------------------------------------------#
def call(jobs, kwargs={}):
    for job in jobs:
        print("Applying script in ",job.path)

        # Specify the base path to the directories containing data
        base_path = job.path + '/case/postProcessing/cuttingLines'
        if not os.path.exists(base_path):
            continue

        # Specify name for the folder containg all four U files for further postProcessing and plotting
        new_folder_name=job.path + '/plots'

        if not os.path.exists(new_folder_name):
            os.makedirs(new_folder_name)
        
        prepare_U.prepare_U(job.path + '/case',new_folder_name)
        plot_Ux_r15.plot_Ux_r15(new_folder_name,"./assets/Python/plot_U/exp_data")
        plot_Ux_r05.plot_Ux_r05(new_folder_name,"./assets/Python/plot_U/exp_data")
        plot_Ur_x03.plot_Ur_x03(new_folder_name,"./assets/Python/plot_U/exp_data")
        plot_Ur_minusx03.plot_Ur_minusx03(new_folder_name,"./assets/Python/plot_U/exp_data")
        plot_forces_check_convergence.plot_forces_check_convergence(job.path + '/case',new_folder_name)
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_plus_056",'AziDown_r25_NewMexico.dat','x=0.3 m, r=0.56 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_minus_056",'AziUp_r25_NewMexico.dat','x=-0.3 m, r=0.56 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_plus_079",'AziDown_r35_NewMexico.dat','x=0.3 m, r=0.79 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_minus_079",'AziUp_r35_NewMexico.dat','x=-0.3 m, r=0.79 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_plus_135",'AziDown_r60_NewMexico.dat','x=0.3 m, r=1.35 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_minus_135",'AziUp_r60_NewMexico.dat','x=-0.3 m, r=1.35 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_plus_185",'AziDown_r82_NewMexico.dat','x=0.3 m, r=1.85 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_minus_185",'AziUp_r82_NewMexico.dat','x=-0.3 m, r=1.85 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_plus_207",'AziDown_r92_NewMexico.dat','x=0.3 m, r=2.07 m')
        plot_azi_probes.plot_azi_probes(job.path + '/case',new_folder_name,"./assets/Python/plot_probes/exp_data","probes_azi_minus_207",'AziUp_r92_NewMexico.dat','x=-0.3 m, r=2.07 m')        