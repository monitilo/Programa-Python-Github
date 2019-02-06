""" Placa"""

import nidaqmx
from pipython import GCSDevice

device = nidaqmx.system.System.local().devices['Dev1']

AOchans = [0, 1]  # TODO: flipper 0 y 1. No estan configurados

detectModes = ['PD']
scanModes = ['ramp scan', 'step scan']
PDchans = [0, 1, 2]  # elegir aca las salidas analog del PD de cada color
shutters = ['532 (verde)', '640 (rojo)', '405 (azul)', '808(NIR)']  # salidas 9,10,11,12
shutterschan = [9, 10, 11, 12]  # las salidas digitales de cada shutter
# TODO: puse la salida 12 es la del nuevo shutter del 808. puede ser otra.

apdrate = 10**5  # TODO: ver velocidad del PD... 5kH dicen

PD_channels = {shutters[0]: 0, shutters[1]: 1, shutters[2]: 2, shutters[3]: 1}  #si rojo e infrarrojo comparten fotodiodo en el set up

pi_device = GCSDevice ()  # Load PI Python Libraries  (thanks Physik Instrumente)
#pi_device.EnumerateUSB()
try:
    pi_device.ConnectUSB ('0111176619')  # Connect to the controller via USB with serial number 0111176619
    print(pi_device.qIDN()) #Out[]: 'Physik Instrumente, E-517, 0111176619, V01.243'
    axes = ['A','B','C']
    allTrue = [True, True, True]
    allFalse = [False, False, False]
    pi_device.ONL([1,2,3],[1,1,1])  # Turn on the Online config (PC master)
    pi_device.DCO(axes, allTrue)  # Turn on the drift compensation mode
    pi_device.SVO (axes, allTrue)  # Turn on servo control
    pi_device.VCO(axes, allFalse)  # Turn off Velocity control. Can't move if ON
    
    pi_device.MOV(axes, [100, 100, 50])  # move away from origin (0,0,0)
    #TOsDO: no necesita estar esto aca. Puedo sacarlo o no
except IOError as e:
    print("I/O error({0}): {1}".format(e.errno, e.strerror))
    print("Can't connect to the platine.")

servo_time = 0.000040  # seconds  # tiempo del servo: 40­µs. lo dice qGWD()