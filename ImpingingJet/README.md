## Impinging Jet

The case setup aims at reproducing the Direct Numerical Simulation
of an impinging jet by ``Dairay et al. (2015), Journal of Fluid Mechanics 764, pp. 362 - 394``, which you can find [here](https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/abs/direct-numerical-simulation-of-a-turbulent-jet-impinging-on-a-heated-wall/0286E7962BABF0CCE6FD2862BCAA57DF).

### Requirements

The case requires the following libraries 
* swak4Foam (libgroovyBC.so)
* boundarycondition (libAddBoundaryConditions.so)

Both can be installed via the initialation script which you can find in assets. 

### TODOS

* Put the boundarycondition library as module linking our git repository
* Remove swak4Foam requirement
* Add OBR testing
