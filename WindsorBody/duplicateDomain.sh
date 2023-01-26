#!/bin/bash -l

# --- prepare case folders
# Copy basic setup
cp -a basicSetup $runDir
cp -a basicSetup tmpDuplicateDir0/

cd tmpDuplicateDir0
cp system/fvSchemes.pre system/fvSchemes
cp system/fvSolution.RANS system/fvSolution
cp $use_control system/controlDict
mkdir -p $logDir
# Rename patch of future internal face
#createPatch -overwrite -dict ./system/createPatchDict.renameBase > $logDir/03_createPatch.renameBase.log 2>&1 || exit 1
# change patch names in boundaryFields of constant directory
sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" ./constant/polyMesh/boundary
cp -a $logDir/ ../$runDir/
# change patch names in boundaryFields of time directory
find ./$timeDir/* -type f -exec sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" {} \;
# # get the number of cells in original mesh
# nCellsOrig=`grep -w -a nCells constant/polyMesh/owner | cut -d ":" -f 3 | cut -d " " -f 1`
cd ..

for ((iCopy=2; iCopy<=$nCaseCopies; iCopy++))
do
    iDuplicateDir=tmpDuplicateDir$(( $iCopy - 1 ))
    cp -a basicSetup $iDuplicateDir/
    cd $iDuplicateDir
    cp system/fvSchemes.pre system/fvSchemes
    cp system/fvSolution.RANS system/fvSolution
    cp $use_control system/controlDict
    mkdir -p $logDir
    # translate Mesh and flowfield in y-direction
    transVec="(0 $( bc -l <<<"($iCopy-1)*1.92" ) 0)"
    transformPoints -rotateFields -translate "$transVec" > $logDir/04_transformpoints_$(($iCopy-1)).log 2>&1 || exit 1
    # # rename all patches, except the right boundary, to have unique patch names for later apllication of mapFieldsPar utility
    # # sed -i "s/^nDomainCopies.*/nDomainCopies    $iCopy;/" system/createPatchDict.renameAddition
    # sed -i "s/_2;/_$iCopy;/g" system/createPatchDict.renameAddition
    # createPatch -overwrite -dict ./system/createPatchDict.renameAddition > $logDir/05_createPatch.renameAddition_$(($iCopy-1)).log 2>&1 || exit 1
    # change patch names in boundaryFields of constant directory
    sed -i "s/\bCFDWT_Left\b/CFDWT_Left_intern/g" ./constant/polyMesh/boundary
    sed -i "s/\bCFDWT_Roof\b/CFDWT_Roof_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bCFDWT_Floor\b/CFDWT_Floor_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bCFDWT_In\b/CFDWT_In_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bCFDWT_Out\b/CFDWT_Out_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bWindsor_Body\b/Windsor_Body_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bWindsor_Base\b/Windsor_Base_$iCopy/g" ./constant/polyMesh/boundary
    sed -i "s/\bWindsor_Pins\b/Windsor_Pins_$iCopy/g" ./constant/polyMesh/boundary
    cp $logDir/* ../$runDir/$logDir/
    # change patch names in boundaryFields of time directory
    find ./$timeDir/* -type f -exec sed -i "s/CFDWT_Left/CFDWT_Left_intern/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/CFDWT_Roof/CFDWT_Roof_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/CFDWT_Floor/CFDWT_Floor_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/CFDWT_In/CFDWT_In_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/CFDWT_Out/CFDWT_Out_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/Windsor_Body/Windsor_Body_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/Windsor_Base/Windsor_Base_$iCopy/g" {} \;
    find ./$timeDir/* -type f -exec sed -i "s/Windsor_Pins/Windsor_Pins_$iCopy/g" {} \;
    cd ..
done 

# --- Copy an Merge mesh
cd $runDir
ln -s ../scripts/ scripts
cp system/fvSchemes.pre system/fvSchemes
cp system/fvSolution.RANS system/fvSolution
cp $use_control system/controlDict
mkdir -p $logDir
rm -r $timeDir/*


for ((iCopy=2; iCopy<=$nCaseCopies; iCopy++))
do
    iDuplicateDir="tmpDuplicateDir$(($iCopy-1))"
    # # Rename patch of future internal face
    # createPatch -overwrite -dict ./system/createPatchDict.renameBase >> $logDir/06_createPatch.renameBase.log 2>&1 || exit 1
    # change patch names in boundaryFields of constant directory
    sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" ./constant/polyMesh/boundary
    # # change patch names in boundaryFields of time directory
    # find ./$timeDir/* -type f -exec sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" {} \;
    # # change number of cells in fields in time directory
    # find ./$timeDir/* -type f -exec sed -i "s/$nCellsOrig/$(($nCellsOrig*$nCaseCopies))/g" {} \;
    # Merge "original" mesh with translated mesh
    mergeMeshes -overwrite . ../$iDuplicateDir/ >> $logDir/07_mergeMeshes.log 2>&1 || exit 1
    # stitch the merged mesh on internal patch faces
    stitchMesh -overwrite CFDWT_Right_intern CFDWT_Left_intern >> $logDir/08_stitchMesh.log 2>&1 || exit 1
    # remove empty internal patches
    createPatch -overwrite -dict ./system/createPatchDict.deleteIntern >> $logDir/09_createPatch.deleteIntern.log 2>&1 || exit 1
    rm ./$timeDir/meshPhi
done
# check mesh
checkMesh > $logDir/10_checkMesh.log 2>&1 || exit 1

cp -a 0.orig/* $timeDir/
cd $timeDir/
cp U U_0
cp k k_0
cp omega omega_0
cp nut nut_0
cp nuTilda nuTilda_0
cd ..
# # change patch names in boundaryFields of time directory
# find ./$timeDir/* -type f -exec sed -i "s/\bCFDWT_Right\b/CFDWT_Right_intern/g" {} \;

# --- Map fields
for ((iCopy=1; iCopy<=$nCaseCopies; iCopy++))
do
    iDuplicateDir="tmpDuplicateDir$(($iCopy-1))"
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

    # mapFieldsPar -sourceTime 'latestTime' -mapMethod direct -patchMapMethod nearestFaceAMI ../tmpDuplicateDir0/ > $logDir/11_mapFieldsPar.log 2>&1 || exit 1 # Error, if OF-v2206 is loaded with gnu/11
    mapFieldsPar -sourceTime 'latestTime' -mapMethod direct -fields '("p.*" "U.*" "k.*" "nut.*" "nuTilda.*" "omega.*")' -targetRegion region0 ../$iDuplicateDir/ >> $logDir/11_mapFieldsPar.log 2>&1 || exit 1 # Error, if OF-v2206 is loaded with gnu/11
done
rm $timeDir/*.unmapped

# setInputParam nCores $nProcs
# decomposePar $use_decompose > $logDir/02_decomposePar.log 2>&1 || exit 1
cd ..
rm -r tmpDuplicateDir*