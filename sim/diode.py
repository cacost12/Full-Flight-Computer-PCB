####################################################################################
#                                                                                  #
# diode.py -- script containing calculations for the Schottky diode parameters     #
#             using discrete forward voltage measurements provided in the          #
#             datasheet                                                            #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 6/15/2023                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
from matplotlib import pyplot as plt
import math
import scipy
import numpy as np


####################################################################################
# Procedures                                                                       #
####################################################################################

# Calculate the current through a diode
def diode_equation( V, alpha, I0 ):
    currents = np.zeros( len( V ) )
    for i, voltage in enumerate( V ):
        currents[i] = I0*( math.exp( alpha*voltage ) - 1 )
    return currents 


####################################################################################
# Calculations                                                                     #
####################################################################################

# Data from datasheet
currents = [0.001, 0.01, 0.1 , 0.2, 0.5  , 0.7 , 1    ] # A
voltages = [0.14 , 0.2 , 0.27, 0.3, 0.355, 0.38, 0.415] # V
currents = np.array( currents )
voltages = np.array( voltages )

# Fit the curve to the data
diode_params, _ = scipy.optimize.curve_fit( diode_equation, 
                                         voltages      ,
                                         currents      )
alpha = diode_params[0]
I0    = diode_params[1]
voltages_fit = np.linspace( voltages[0], voltages[-1], num = 1000 )
currents_fit = diode_equation( voltages_fit, alpha, I0 )

# Plot raw data
plt.figure()
plt.scatter( voltages, currents, marker="o")
plt.plot( voltages_fit, currents_fit, color="r" )
plt.title( "Schottky Diode Current Versus Forward Voltage" )
plt.xlabel( "Forward Voltage, V")
plt.ylabel( "Current, A" )
plt.grid()
plt.show()

# Display the diode parameters
print( "Diode Parameters: \n")
print( "Saturation Current: " + str( I0    ) )
print( "Thermal Voltage   : " + str( alpha ) )


####################################################################################
# EOF                                                                              #
####################################################################################