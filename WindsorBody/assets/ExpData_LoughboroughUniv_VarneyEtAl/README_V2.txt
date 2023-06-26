This is the README file for the dataset for the square-back variation of the 25% scale Windsor Model, collated by Max Varney on 27/10/2020. More information can be found in the following publications:
- "Base Drag Reduction for Squareback Road Vehicles", Varney, M., PhD Thesis, Loughborough University, https://repository.lboro.ac.uk/articles/thesis/Base_drag_reduction_for_squareback_road_vehicles/11823759
- avia, G., Passmore, M., Varney, M., & Hodgson, G. (2020). Salient three-dimensional features of the turbulent wake of a simplified square-back vehicle. Journal of Fluid Mechanics, 888, A33, https://repository.lboro.ac.uk/articles/journal_contribution/Salient_three-dimensional_features_of_the_turbulent_wake_of_a_simplified_square-back_vehicle/11669679

Data was collected in the Large Wind Tunnel at Loughborough University, a 2.5 m^2, closed working section, fixed-ground, open-return tunnel. Further details can be found in:
- Johl, G., Passmore, M., & Render, P. (2004). Design methodology and performance of an indraft wind tunnel. The Aeronautical Journal (1968), 108(1087), 465-473, https://repository.lboro.ac.uk/articles/journal_contribution/Design_methodology_and_performance_of_an_indraft_wind_tunnel/9224171

The CAD models for the two referenced variations of the Windsor Model (square-back with and without wheels), the mounting hardware and the wind tunnel are included in both .STEP and .STL formats, with the units in mm.

For all experiments included in this dataset, the zero degree yaw condition was found by yawing the model in 0.1 degree increments until a symmetric base pressure was achieved (prior to the start of testing) The yawed data provided is relative to this aerodynamic 0 degree yaw.

No corrections (for example blockage) have been applied to the data. All the data is presented in SI units and in accordance with SAE vehicle aerodynamics terminology (J1594). The origin is positioned at mid-track, mid-wheelbase (of the with wheels variation) on the tunnel floor. X is positive rearward, Z upward and Y to the right of the model. Positive yaw is then defined as nose towards positive Y.

The data is presented in two sets:
Set A Relates to the square-back Windsor Model with and without wheels at aerodynamic 0 degree yaw.  It contains data collected using tomographic PIV plus additional planes of PIV data that provide higher spatial resolution.
	NOTE: The stereo cross-plane data (X = * m) with wheels, uses a different wheel mounting system than that provided in the CAD models. To avoid complication we have not included this geometry in the dataset as it is assumed not to have a large effect on the wake structure. The wheels were stationary for the acquisition of these additional planes, and further details of this experiment can be found in the following paper:
	- Pavia G., Passmore M. (2018) Characterisation of Wake Bi-stability for a Square-Back Geometry with Rotating Wheels. In: Wiedemann J. (eds) Progress in Vehicle Aerodynamics and Thermal Management. FKFS 2017. Springer, Cham, https://repository.lboro.ac.uk/articles/chapter/Characterisation_of_wake_bi-stability_for_a_square-back_geometry_with_rotating_wheels/9211862
Set B Provides additional data for the square-back Windsor Model at 2.5, 5 and 10 degrees yaw. For zero degree yaw data, researchers are referred to Set A. 

The data within both set A and B is split into '_Mean' and '_Instantaneous' for both the Pressure and Flow Field data, with only '_Mean' data supplied for the Forces. The Force and Pressure data has been captured over a total sample time of 300 seconds. These acquisitions were performed during the same test run, but are not correlated in time. The Force measurements were sampled at 300Hz, whereas the Pressure data was sampled at 260Hz. The PIV measurements were performed during a different test campaign, with individual nominal velocities, sample lengths, and frequencies shown below. The data presented in the '_Mean' folders is the arithmetic mean of that presented in the '_Instantaneous' folders.
	NOTE: Configuration: NW = No wheels, WW = With wheels.  Researcher: MV = Dr Max Varney,  GP = Dr Giancarlo Pavia

Configuration	Plane		Nominal Velocity (m/s)	Sample Length	Sample Frequency (Hz)	Yaw Angles (deg)	Researcher
WW		TOMO		30			1000		5			0, 2.5, 5, 10		MV
NW		TOMO		30			1000		5			0, 2.5, 5, 10		MV
NW		Y = 0 m		40			1000		5			0			MV
WW		Y = 0 m		40			1000		5			0			MV
NW		Z = 0.194 m	40			1000		5			0, 2.5, 5, 10		MV
WW		Z = 0.194 m	40			1000		5			0, 2.5, 5, 10		MV
NW		X = 0.628 m 	40			2000		15			0			GP
NW		X = 0.917 m 	40			2000		15			0			GP
WW		X = 0.628 m 	40			2000		15			0			GP
WW		X = 0.917 m 	40			2000		15			0			GP

The tomographic testing uses a lower freestream velocity to ensure that there was sufficient seeding (helium-filled soap bubbles) in the region of interest. For more detail on the PIV set-ups, please refer to the aforementioned publications.

All the '_Mean' and '_Instantaneous' folders contain Comma Separated Variable (.csv) files for each configuration for ease of parsing with your desired programming language. Example MATLAB code has been provided (tested in R2019a) that reads both the '_Mean' and '_Instantaneous' .csv files for the Pressure and Flow Field measurements, plotting them accordingly.

The 'Force_Mean' folder contains a .csv file for each configuration, with the mean taken over the 300 second acquisition. This file includes the velocity, ambient temperature, ambient pressure, calculated air density, yaw angle, the 3 force and 3 moments (taken about mid-wheelbase mid-track and on the tunnel floor), the model frontal area, model wheelbase, the calculated force and moment coefficients.

The 'Pressure_Mean' folder contains two sets of .csv files. '_Tapping_Map', presents the x, y and z positions of the Pressure tappings, the group that they belong to (1 - Vertical Centerline, 2 - Upper Glasshouse, 3 - Front Bumper, 4 - Base) and the associated Pressure tapping number. '_Averages', contains the mean, '_MeanCp', and RMS of the deviation, '_RMSCp'.

The 'Pressure_Instantaneous' folder contains a .csv file for each configuration. It also contains the same '_Tapping_Map' csv files provide with the mean Pressures to prevent the need to download both datasets. In this instance each column is a Pressure tapping location and each row is a time instance. Two separate pressure scanners were used during these experiments that cannot be accurately synchronised. As a result if any cross correlation is performed by the user this should ONLY be performed on tapping numbers 1-64 OR 65-128, correlations performed between these groups will result in significant errors.

The 'FlowField_Mean' folder contains a .csv file for each configuration and plane. Each .csv file includes the x, y and z coordinate of every vector, the mean and rms of the u, v  and w components and the velocity magnitude. Invalid vectors are marked in the dataset with a value of -9999  at the XYZ location (Invalid vectors arise in experimental data due to seeding, image quality or processing problems). The FlowField_Example_Code hides the invalid vectors during plotting.

The 'FlowField_Instantaneous' folder contains the same file structure as 'FlowField_Mean' but with the columns representing time steps, indicated by the column header. A simple way to read this is demonstrated in FlowField_Example_Code.


=== CONTRIBUTORS ===

Original Author
Max Varney (https://www.linkedin.com/in/max-varney/)

Current Maintainer
Conor Crickmore (c.j.crickmore@lboro.ac.uk)


=== CHANGELOG ===

V1, 27/10/2020
- Initial release

V2, 23/06/2021
- Corrected error in the compilation of the Set A FlowField_Mean folder involving the v-component of velocity in the cross-plane (X = * m) data
- Corrected error in the compilation of the Set A FlowField_Mean folder involving the RMS of the u-component of velocity in the cross-plane (X = * m) data
- Addressed inconsistencies with the origin position in the cross-plane (X = * m) data
- Addressed inconsistencies with the origin position in the pressure tapping map
- Updated CAD models to include higher quality .STEP and .STL options
