####################################################################################
#                                                                                  #
# ignition.py -- script containing calculations for the MOSFETS used within the    #
#                ignition circuitry                                                #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 6/15/2023                                                                  #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import math
import numpy as np
from matplotlib import pyplot as plt


####################################################################################
# Globals                                                                          #
####################################################################################
ERROR_THRESHOLD = 0.01
MAX_ITERATIONS  = 1000


####################################################################################
# Objects                                                                          #
####################################################################################

# N-Channel Mosfet transistor
class NMOS:

    def __init__( self, kn, Vt ):
        self.kn = kn
        self.Vt = Vt

    def calc_drain_current( self, Vg, Vd, Vs ):
        Vov = Vg - Vs - self.Vt
        if ( Vov < 0 ):
            return 0
        elif ( Vov < (Vd - Vs) ):
            return 0.5*self.kn*(Vov**2)
        else:
            return self.kn*( Vov*(Vd - Vs) - 0.5*((Vd - Vs)**2) )

    def calc_drain_currents( self, Vg, Vd, Vs ):
        currents = np.zeros( len( Vg ) )
        for i, voltage in enumerate( Vg ):
            currents[i] = self.calc_drain_current( Vg[i], Vd[i], Vs[i] )
        return currents

    def calc_drain_current_sat( self, Vg, Vs ):
        return 0.5*self.kn*( (Vg - Vs - self.Vt)**2 )
## NMOS ##

# Schottky Diode
class Diode:

    def __init__( self, I0, alpha ):
        self.I0    = I0
        self.alpha = alpha

    def calc_current( self, VF ):
        return self.I0*( math.exp( self.alpha* VF ) - 1 )
    
    def calc_currents( self, VF ):
        currents = np.zeros( len( VF ) )
        for i, voltage in enumerate( VF ):
            currents[i] = self.calc_current( voltage )
        return currents

    # Forward Voltage Drop
    def calc_voltage( self, I ):
        return math.log( (I/self.I0) + 1 )/self.alpha
## Diode ##


####################################################################################
# Calculations                                                                     #
####################################################################################

# Setup devices
mux_diode  = Diode( 0.004197, 13.28 )
drive_nmos = NMOS( 4.2, 1.0 )
cont_nmos  = NMOS( 0.159, 1.5 )
Rp         = 1      # Parasitic resistance, Ohm
Rcont      = 10_000 # Continuity pull-up resistor

# Range of input voltages
input_voltages = np.linspace( 3.7, (3.7*4), 100 )
drive_Vds      = np.zeros( len(input_voltages)  )
drive_currents = np.zeros( len(input_voltages)  )
diode_VFs      = np.zeros( len(input_voltages)  )
cont_voltages  = np.zeros( len(input_voltages)  )

# Solve for the drive voltage 
for i, voltage in enumerate( input_voltages ):

    # Setup iterative solver parameters
    error          = 100   # arbitrary large initialization value
    current_actual = 0.1   # Calculated current 
    current_guess  = 0.1   # Next current guess to evaluate
    num_iter       = 0     # Iteration Number
    learn_rate     = 0.01  # Step size control for stability
    print( "Solving for battery voltage {:.3f}V".format( voltage ) )

    # Solver
    while ( error >= ERROR_THRESHOLD and num_iter < MAX_ITERATIONS ):
        diode_VF       = mux_diode.calc_voltage( current_guess )
        Vd             = voltage - diode_VF - (current_guess*Rp)
        current_actual = drive_nmos.calc_drain_current( 3.3, Vd, 0 )
        error          = ( abs( current_actual - current_guess ) )/current_actual
        current_guess  = current_guess + learn_rate*( current_actual - current_guess )
        num_iter       += 1

    if ( num_iter == MAX_ITERATIONS ):
        print( "Solver failed to converge" )
    else:
        print( "Solution converged in {:d} iterations".format( num_iter ) )
    
    # Record results
    drive_Vds[i]      = Vd
    drive_currents[i] = current_guess
    diode_VFs[i]      = diode_VF


# Visualize Results
plt.figure()
plt.plot( input_voltages, drive_currents )
plt.title( "Drive Current vs Battery Voltage" )
plt.xlabel( "Battery Voltage, V")
plt.ylabel( "Drive Current, A" )
plt.grid()
plt.show()

plt.figure()
plt.plot( input_voltages, drive_Vds )
plt.title( "Drive Drain Voltage vs Battery Voltage" )
plt.xlabel( "Battery Voltage, V" )
plt.ylabel( "Drive Drain Voltage, V" )
plt.grid()
plt.show()

plt.figure()
plt.plot( input_voltages, diode_VFs )
plt.title( "Diode forward voltage vs Battery Voltage" )
plt.xlabel( "Battery Voltage, V" )
plt.ylabel( "Diode Forward Voltage" )
plt.grid()
plt.show()

# Solve for the continuity signal
for i, voltage in enumerate( input_voltages ):
    Vov   = voltage - cont_nmos.Vt
    if ( Vov < 0 ):
        current = 0
    else:
        current = cont_nmos.calc_drain_current_sat( voltage, 0 )
    Vcont = 3.3 - current*Rcont
    if ( Vov > Vcont ):
        b = Vov + (1/(cont_nmos.kn*Rcont))
        c = 2*3.3/(cont_nmos.kn*Rcont)
        cont_voltages[i] = b - math.sqrt( b**2 - c)
    else:
        cont_voltages[i] = Vcont

# Display Continuity voltage results
plt.figure()
plt.plot( input_voltages, cont_voltages )
plt.title( "Continuity Output Voltage versus Battery Voltage" )
plt.xlabel( "Battery Voltage, V" )
plt.ylabel( "Continuity Output Voltage, V" )
plt.grid()
plt.show()


####################################################################################
# EOF                                                                              #
####################################################################################