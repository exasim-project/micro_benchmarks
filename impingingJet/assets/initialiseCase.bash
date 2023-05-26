#!/bin/bash

# Check if swak4Foam is installed
installSwak=false
if ! command -v funkySetBoundaryField  &> /dev/null
then
	echo ""
	echo "Swak4Foam seems not to be installed, or "
        echo "the OpenFoam module not loaded." 	
	echo "I Proceed with the installation of swak4Foam."
	echo ""
	echo "Requirements:"
	echo " * bison "
	echo " * bear  "
	read -r -p "Are you sure? [y/N] " response
	case "$response" in 
		[yY][eE][sS]|[yY]) 
        		installSwak=true
        		;;
    		*)
        		insallSwak=false
        		;;
		esac
fi

if $installSwak ; then

# Check if Mercurial is installed
if ! command -v hg &> /dev/null
then
	echo ""
	echo "You need to install mercurial for downloading"
        echo "and installing swak4foam!"
        exit
fi
# Download swak4foam
rm -rf swak4Foam
hg clone http://hg.code.sf.net/p/openfoam-extend/swak4Foam swak4Foam
cd swak4Foam
hg update develop

# Check if OpenFoam environment is loaded
if ! command -v simpleFoam  &> /dev/null
then
	echo ""
	echo "OpenFOAM environment is not loaded!" 
	echo "I cannot procede with the the compilation of swak4Foam"
	exit
fi

# Compile swak4Foam
./Allwmake

echo ""
echo "Do you allow me to add the environment variable"
echo "export SWAK4FOAM_SRC=$PWD/Libraries"
read -r -p "to your .bashrc?" response
case "$response" in 
	[yY][eE][sS]|[yY]) 
                echo "export SWAK4FOAM_SRC=$PWD/Libraries" >> $HOME/.bashrc
       		;;
	*)
       		echo "then you will have to do it yourself!"
		read -p "Press enter to continue"
       		;;
esac
cd ..
fi

# Compile the boundary condition
if ! command -v simpleFoam  &> /dev/null
then
	echo "" 
	echo "OpenFOAM environment is not loaded:" 
	echo "I cannot compile the boundary conditions!"
	exit
fi
cd boundarycondition
wmake
cd ..
