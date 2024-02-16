#!/bin/bash
# This is a shell script to concatenate the windsor body case n times at the right hand side boundary.
# It relies on OpenFOAM (v2206) utilities to manipulate the domain and fields.
#
# The number of concatenations/domain copies can be given as argument of option -n.
# If fields should be concatenated too, the option -f can be used. Without -f option only the mesh is manipulated.
#
# Options:    -n          number of conatenated domains (i.e. -n 3 results in 3 windsor bodies next to each other)
#             -f          concatenate fields of latest time driectory too
#
# Script developer : Louis Fliessbach (louis.fliessbach@upstream-cfd.com)
#
# Last updated : 13.02.2023

# set default number of concatenations
nCaseCopies=2
concatFields=false
overwriteFlag='-overwrite'
# --- get options
while getopts ":n:f" opt; do
  case $opt in
    n)
      echo "-n, $OPTARG" >&2
      nCaseCopies=$OPTARG
      ;;
    f)
      echo "-f, concatenate fields too." >&2
      concatFields=true
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done
echo
echo "Concatenate domain $nCaseCopies times ..."
echo

# --- prepare case folder
# Copy basic setup
runDir=$(pwd)
echo "Concatenate domain of case"
echo "$runDir"
echo
timeDir="0"
if $concatFields && [[ ${timeDir} == '' ]]; then
    echo "No time directory present! Concatenation only effects mesh."
    concatFields=false
else
    echo "Concatenate/map fields of time $timeDir"
fi

if ! $concatFields && [[ -d ${timeDir} ]]; then
    echo "Warning ${timeDir} present, and concatFields not set" 
    echo "temporarily moving  ${timeDir} to ${timeDir}.bck"
    mv $timeDir $timeDir.bck
fi

echo
logDir="logFiles"
mkdir -p $logDir

cd ..
# --- create temporary directories with translated domain
for ((iCopy=1; iCopy<=$nCaseCopies; iCopy++))
do
    echo "copy domain $iCopy of $nCaseCopies"

    iTmpDir=tmpDir$(( $iCopy - 1 ))
    cp -a $runDir $iTmpDir/
    cd $iTmpDir

    if [ $iCopy -eq 1 ]; then
        # Rename patch of future internal face
        # change patch names in boundaryFields of constant directory
        sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" ./constant/polyMesh/boundary
        if $concatFields; then
            # change patch names in boundaryFields of time directory
            find ./$timeDir/* -type f -exec sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" {} \;
        fi
    else
        # --- translate Mesh and flowfield in y-direction
        transVec="(0 $( bc -l <<<"($iCopy-1)*1.92" ) 0)"
    echo "call transformPoints with $transVec in $PWD, placing logs in $logDir"
        transformPoints -rotateFields -translate "$transVec" > $logDir/01_transformpoints_$(($iCopy-1)).log 2>&1 || exit 1
        # --- rename all patches, except the right boundary, to have unique patch names for later apllication of mapFieldsPar utility
        # change patch names in boundaryFields of constant directory
        sed -i "s/\bCFDWT_Left\b/CFDWT_Left_intern/g" ./constant/polyMesh/boundary
        if $concatFields; then
            # change patch names in boundaryFields of time directory
            find ./$timeDir/* -type f -exec sed -i "s/CFDWT_Left/CFDWT_Left_intern/g" {} \;
        fi
        # array of non intern patches
        patchesNonIntern=("CFDWT_Roof" "CFDWT_Floor" "CFDWT_In" "CFDWT_Out" "Windsor_Body" "Windsor_Base" "Windsor_Pins")
        # change patch names in boundaryFields of constant directory
        for patch in "${patchesNonIntern[@]}"; do
            sed -i "s/\b${patch}\b/${patch}_${iCopy}/g" ./constant/polyMesh/boundary
        done
        if $concatFields; then
            # change patch names in boundaryFields of time directory
            for patch in "${patchesNonIntern[@]}"; do
                find ./$timeDir/* -type f -exec sed -i "s/\b${patch}\b/${patch}_$iCopy/g" {} \;
            done
        fi
        cp $logDir/* $runDir/$logDir/
    fi
    cd ..
done 
echo "Done translating all $nCaseCopies domains"

# --- Copy and Merge mesh
cd $runDir
if $concatFields; then
    # Delete fields in time directory
    rm -r $timeDir/*
fi

echo "Start merging all $nCaseCopies domains"
for ((iCopy=2; iCopy<=$nCaseCopies; iCopy++))
do
    iTmpDir="tmpDir$(($iCopy-1))"
    # # Rename patch of future internal face
    # change patch names in boundaryFields of constant directory
    sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" ./constant/polyMesh/boundary
    # Merge "original" mesh with translated mesh
    echo "call mergeMeshes with $overwriteFlag in $PWD, placing logs in $logDir"
    mergeMeshes $overwriteFlag . ../$iTmpDir/ >> $logDir/02_mergeMeshes.log 2>&1 || exit 1
    # stitch the merged mesh on internal patch faces
    echo "call stitchMesh with $overwriteFlag in $PWD, placing logs in $logDir"
    stitchMesh $overwriteFlag CFDWT_Right_intern CFDWT_Left_intern >> $logDir/03_stitchMesh.log 2>&1 || exit 1
    # remove empty internal patches
    echo "call stitchMesh with $overwriteFlag in $PWD, placing logs in $logDir"
    createPatch $overwriteFlag -dict ./system/createPatchDict.deleteIntern >> $logDir/04_createPatch.deleteIntern.log 2>&1 || exit 1
    rm ./$timeDir/meshPhi || true
    echo "Done adding $iCopy domain"
done
echo "Done merging all $nCaseCopies domains"

if ! $concatFields && [[ -d ${timeDir} ]]; then
    echo "Found time directory $timeDir. Cleaning up if empty"
    rmdir $timeDir
fi

if $concatFields; then
    echo "Start concatenating fields"
    cp -a 0.orig/* $timeDir/
    cd $timeDir/
    cp U U_0
    cp k k_0
    cp omega omega_0
    cp nut nut_0
    cp nuTilda nuTilda_0
    cd ..

    # --- Map fields
    for ((iCopy=1; iCopy<=$nCaseCopies; iCopy++))
    do
        iTmpDir="tmpDir$(($iCopy-1))"
        if [ $iCopy -eq 1 ]; then
            # map flow fields of "original" case to "left side" of new merged mesh
            cp system/mapFieldsDict.left system/mapFieldsDict
        elif [ $iCopy -eq $nCaseCopies ]; then
            # map flow fields of translated case to "right side" of new merged mesh
            cp system/mapFieldsDict.right system/mapFieldsDict
            sed -i "s/_2/_$iCopy/g" system/mapFieldsDict
        else
            # map flow fields of translated case to "right side" of new merged mesh
            cp system/mapFieldsDict.middle system/mapFieldsDict
            sed -i "s/_2/_$iCopy/g" system/mapFieldsDict
        fi

    echo "call mapFieldsPar in $PWD, placing logs in $logDir"
        # mapFieldsPar -sourceTime 'latestTime' -mapMethod direct -patchMapMethod nearestFaceAMI ../tmpDir0/ > $logDir/11_mapFieldsPar.log 2>&1 || exit 1 # Error, if OF-v2206 is loaded with gnu/11
        mapFieldsPar -sourceTime 'latestTime' -mapMethod direct -fields '("p.*" "U.*" "k.*" "nut.*" "nuTilda.*" "omega.*")' -targetRegion region0 ../$iTmpDir/ >> $logDir/06_mapFieldsPar.log 2>&1 || exit 1 # Error, if OF-v2206 is loaded with gnu/11
    done
    echo "Done concatenating fields"
fi

if ! $concatFields && [[ -d ${timeDir}.bck ]]; then
    echo "Restoring time directory ${timeDir}" 
    mv $timeDir.bck $timeDir
fi

for ((iCopy=0; iCopy<=$nCaseCopies; iCopy++))
do
    if [[ -d ../tmpDir$iCopy ]]; then
        echo "cleaning up tmpDir directory tmpDir$iCopy" 
        rm -r ../tmpDir*
    fi 
done 

