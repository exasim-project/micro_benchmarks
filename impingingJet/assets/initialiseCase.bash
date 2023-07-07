#!/bin/bash
mkdir -p requirements; cd requirements

# Compile the boundary condition
if [[ -z "${FOAM_RUN}" ]]
then
	echo "OpenFOAM environment is not loaded:" 
	echo "I cannot compile the boundary conditions!"
	exit
fi
cd boundarycondition
wmake
cd ..
