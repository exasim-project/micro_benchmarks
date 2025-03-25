import numpy as np
import matplotlib.pyplot as plt

# Clear command window
import os
os.system('cls' if os.name == 'nt' else 'clear')

# import data of spectral DNS case
DNS = {}
DNS['mean'] = np.genfromtxt('../../../benchmarkData/spectralDNS/mean.dat')
DNS['var'] = np.genfromtxt('../../../benchmarkData/spectralDNS/var.dat')  

# extract some data from the DNS case array, so that they have the same
# structure as the OpenFOAM case
ny = DNS['mean'][:,0].size
DNS['U'] = DNS['mean'][1:(ny-3)//2+1,0:2]
DNS["u'"] = DNS['var'][1:(ny-3)//2+1,0:2];    DNS["u'"][:,1] = DNS["u'"][:,1]**0.5
DNS["v'"] = DNS['var'][1:(ny-3)//2+1,[0,2]];  DNS["v'"][:,1] = DNS["v'"][:,1]**0.5
DNS["w'"] = DNS['var'][1:(ny-3)//2+1,[0,3]];  DNS["w'"][:,1] = DNS["w'"][:,1]**0.5


# some bulk statistics of the spectral DNS case
DNS['delra_ni'] = 0.00275052
DNS['utau'] = 0.05275557

# import data of ISTM OpenFOAM run
OpenFOAM = {}
OpenFOAM['U']      = np.loadtxt('../../../benchmarkData/ISTMopenFOAMrun/Uf.xy', dtype=np.float64)
OpenFOAM["u'"] = np.loadtxt('../../../benchmarkData/ISTMopenFOAMrun/u.xy', dtype=np.float64)
OpenFOAM["v'"] = np.loadtxt('../../../benchmarkData/ISTMopenFOAMrun/v.xy', dtype=np.float64)
OpenFOAM["w'"] = np.loadtxt('../../../benchmarkData/ISTMopenFOAMrun/w.xy', dtype=np.float64)
# some bulk statistics of the ISTM OpenFOAM run
PGOF = np.genfromtxt('../../../benchmarkData/ISTMopenFOAMrun/pGrad.txt')
MPGOP = np.average(PGOF)
OpenFOAM['utau'] = np.sqrt(MPGOP)
OpenFOAM['nu'] = 1.45105e-04
OpenFOAM['delta_ni'] = OpenFOAM['nu']/OpenFOAM['utau']

# import data of ISTM OpenFOAM run
#OpenFOAM2 = {}
#OpenFOAM2['U']      = np.loadtxt('../../../view/base/linear_solver/GAMGnone/case/graphs/3.9/Uf.xy', dtype=np.float64)
#OpenFOAM2["u'"] = np.loadtxt('../../../view/base/linear_solver/GAMGnone/case/graphs/3.9/u.xy', dtype=np.float64)
#OpenFOAM2["v'"] = np.loadtxt('../../../view/base/linear_solver/GAMGnone/case/graphs/3.9/v.xy', dtype=np.float64)
#OpenFOAM2["w'"] = np.loadtxt('../../../view/base/linear_solver/GAMGnone/case/graphs/3.9/w.xy', dtype=np.float64)
# some bulk statistics of the ISTM OpenFOAM run
#PGOF2 = np.genfromtxt('../../../view/base/linear_solver/GAMGnone/case/graphs/3.9/pGrad.txt')
#MPGOP2 = np.average(PGOF2)
#OpenFOAM2['utau'] = np.sqrt(MPGOP2)
#OpenFOAM2['nu'] = 1.45105e-04
#OpenFOAM2['delta_ni'] = OpenFOAM2['nu']/OpenFOAM2['utau']

# Plot some data
for key in ['U', "u'", "v'", "w'"]:
    plt.figure()
#    plt.semilogx(OpenFOAM2[key][:, 0], OpenFOAM2[key][:, 1], 'k-', label='OpenFoam Current')
    plt.semilogx(OpenFOAM[key][:, 0], OpenFOAM[key][:, 1], 'r-', label='OpenFoam ISTM')
    plt.semilogx(DNS[key][2:,0], DNS[key][2:,1], 'b--', label='spectral DNS')
    plt.legend(loc='best')
    plt.xlabel('$y/h$', fontsize=30)
    plt.ylabel(key+'/U_b', fontsize=30)
    plt.show()
