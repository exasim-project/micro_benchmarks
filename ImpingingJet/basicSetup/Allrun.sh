blockMesh > blockMesh.log
topoSet > topoSet.log
createPatch -overwrite > createPatch.log
sed -i "/topSolidWall/,/\}/ s/        type            patch;/        type            wall;/" ./constant/polyMesh/boundary
decomposePar > decomposePar.log
mpirun --use-hwthread-cpus --bind-to core --map-by core -report-bindings pimpleFoam -parallel > pimpleFoam.log
wait
