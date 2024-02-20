blockMesh > blockMesh.log
topoSet > topoSet.log
createPatch -overwrite > createPatch.log
cp -r 0.orig 0
decomposePar -force  > decomposePar.log
mpirun --np 256 --use-hwthread-cpus --bind-to core --map-by core -report-bindings pimpleFoam -parallel > pimpleFoam.log
wait
