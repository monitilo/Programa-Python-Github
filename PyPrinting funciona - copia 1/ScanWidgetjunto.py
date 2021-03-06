﻿# %% ScanWidget
from pyqtgraph.Qt import QtCore, QtGui

import tkinter as tk
from tkinter import filedialog
import os

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
import pyqtgraph.ptime as ptime

import numpy as np
import time
import matplotlib.pyplot as plt
from scipy import ndimage
#from scipy import stats

from Placa import *
import Trace
from otrasfunciones import *


class ScanWidget(QtGui.QFrame):

    def __init__(self, main, device, *args, **kwargs):  # agregue device

        super().__init__(*args, **kwargs)  #se usa??? LPM

        self.main = main
        self.nidaq = device

# ---  COSAS DE PRINTIG!

    # Cosas para la rutina de imprimir. Grid

    # umbral
        self.umbralLabel = QtGui.QLabel('Umbral')
        self.umbralEdit = QtGui.QLineEdit('10')
        self.umbralEdit.setFixedWidth(40)
        self.umbralEdit.setToolTip('promedios de valores nuevo/anteriores ')
        self.umbralLabel.setToolTip('promedios de valores nuevo/anteriores ')

    # Tiempo de espera maximo
        self.tmaxLabel = QtGui.QLabel('t max (s)')
        self.tmaxEdit = QtGui.QLineEdit('60')
        self.tmaxEdit.setFixedWidth(40)
        self.tmaxEdit.setToolTip('Tiempo que espera un envento. Si no, sigue')
        self.tmaxLabel.setToolTip('Tiempo que espera un envento. Si no, sigue')

    # Defino el tipo de laser que quiero para imprimir
        self.grid_laser = QtGui.QComboBox()
        self.grid_laser.addItems(shutters)
        self.grid_laser.setCurrentIndex(0)
        self.grid_laser.setToolTip('Elijo el shuter para IMPRIMIR la grilla')
        self.grid_laser.setFixedWidth(80)
        self.grid_laser.activated.connect(
                                    lambda: self.color_menu(self.grid_laser))
        self.color_menu(self.grid_laser)
        grid_laser_label = QtGui.QLabel('<strong> Print Laser')

    # Buttons
        self.cargar_archivo_button = QtGui.QPushButton('Cargar Archivo')
        self.cargar_archivo_button.clicked.connect(self.grid_read)
        self.cargar_archivo_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        self.cargar_archivo_button.setToolTip('Carga el archivo con la grilla, y lo puede plotear para ver si esta bien')

    # Print button. Que en realidad solo crea la carpeta
        self.imprimir_button = QtGui.QPushButton('IMPRIMIR (crea carpeta)')
        self.imprimir_button.setCheckable(True)
        self.imprimir_button.clicked.connect(self.grid_create_folder)
        self.imprimir_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.imprimir_button.setToolTip('En realidad solo crea la carpeta. El mundo es una gran mentira.')
#                "QPushButton:checked {color: white; background-color: blue;}")

    # desides if plot the positions in the grid to print. Just for  be sure
        self.grid_plot_check = QtGui.QCheckBox('plot_test?')
        self.grid_plot_check.clicked.connect(self.grid_plot)

    # Print button. Que en realidad solo crea la carpeta
        self.next_button = QtGui.QPushButton('Next ►')
        self.next_button.setCheckable(False)
        self.next_button.clicked.connect(self.grid_start)
        self.next_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.next_button.setToolTip('Empeiza o continua la grilla')

    # go ref button.
        self.go_ref_button = QtGui.QPushButton('go reference')
        self.go_ref_button.setCheckable(False)
        self.go_ref_button.clicked.connect(self.go_reference)
        self.go_ref_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.go_ref_button.setToolTip('Va a la referencia seteada')
        self.go_ref_button.setFixedWidth(80)

    # set reference button.
        self.set_ref_button = QtGui.QPushButton('set reference')
        self.set_ref_button.setCheckable(False)
        self.set_ref_button.clicked.connect(self.set_reference)
        self.set_ref_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.set_ref_button.setToolTip('setea la referencia')
        self.set_ref_button.setFixedWidth(150)

        self.scan_check = QtGui.QCheckBox('scan?')
        self.scan_check.clicked.connect(self.scan_change)
        self.scan_check.setStyleSheet("color: green; ")
        self.scan_change()

    # particulas totales
        self.particulasLabel = QtGui.QLabel('Cantidad de puntos')
        self.particulasEdit = QtGui.QLabel('0')
        self.particulasEdit.setFixedWidth(40)
        self.particulasEdit.setToolTip('Cantidad de particulas totales a imprimir')
        self.particulasLabel.setToolTip('Cantidad de particulas totales a imprimir')
        self.particulasEdit.setStyleSheet(
                                        " background-color: rgb(200,200,200)")
    # Indice actual
        self.indice_impresionLabel = QtGui.QLabel('Indice de impresion')
        self.indice_impresionEdit = QtGui.QLabel('0')
        self.indice_impresionEdit.setFixedWidth(40)
        self.indice_impresionEdit.setStyleSheet(
                                        " background-color: rgb(200,200,200)")

    # La grid con las cosas de printing. Mas abajo entra en el dock
        self.grid_print = QtGui.QWidget()
        grid_print_layout = QtGui.QGridLayout()
        self.grid_print.setLayout(grid_print_layout)
        grid_print_layout.addWidget(self.cargar_archivo_button,   0, 1, 2, 1)
        grid_print_layout.addWidget(self.imprimir_button,         0, 2, 2, 1)
        grid_print_layout.addWidget(self.next_button,             2, 2, 2, 1)
        grid_print_layout.addWidget(self.go_ref_button,           2, 1)
        grid_print_layout.addWidget(self.set_ref_button,          3, 1)
        grid_print_layout.addWidget(grid_laser_label,             0, 3, 1, 2)
        grid_print_layout.addWidget(self.grid_laser,              1, 3, 1, 2)
        grid_print_layout.addWidget(QtGui.QLabel('Umbral'),             3, 3)
        grid_print_layout.addWidget(self.umbralEdit,              4, 3)
        grid_print_layout.addWidget(self.tmaxLabel,               3, 4)
        grid_print_layout.addWidget(self.tmaxEdit,                4, 4)
        grid_print_layout.addWidget(self.scan_check,              4, 2)
        grid_print_layout.addWidget(self.particulasLabel,         0, 5)
        grid_print_layout.addWidget(self.particulasEdit,          1, 5)
        grid_print_layout.addWidget(self.indice_impresionLabel,   2, 5)
        grid_print_layout.addWidget(self.indice_impresionEdit,    3, 5)
        grid_print_layout.addWidget(self.grid_plot_check,            4, 1)

    # Cosas para la parte del foco

    # Defino el tipo de laser que quiero para hacer foco
        self.focus_laser = QtGui.QComboBox()
        self.focus_laser.addItems(shutters)
        self.focus_laser.setCurrentIndex(2)
        self.focus_laser.setToolTip('Elijo el shuter para HACER FOCO')
        self.focus_laser.setFixedWidth(80)
        self.focus_laser.activated.connect(
                                    lambda: self.color_menu(self.focus_laser))
        self.color_menu(self.focus_laser)
        focus_laser_label = QtGui.QLabel('<strong> Focus Laser')


    # Boton para Lockear el foco
        self.focus_lock_button = QtGui.QPushButton('Lock Focus')
        self.focus_lock_button.setCheckable(False)
        self.focus_lock_button.clicked.connect(self.focus_lock_focus_rampas)
        self.focus_lock_button.setToolTip('guarda el patron en el z actual')
        self.focus_lock_button.setStyleSheet(
                "QPushButton { background-color: rgb(254,100,100) ; }"
                "QPushButton:pressed { background-color: blue; }")

    # Boton de Autocorrelacion, con el foco ya lockeado
        self.focus_autocorr_button = QtGui.QPushButton('Autocorrelacion')
        self.focus_autocorr_button.setCheckable(False)
        self.focus_autocorr_button.clicked.connect(self.focus_autocorr_rampas)
        self.focus_autocorr_button.setToolTip('guarda el patron nel z actual')

    # Go to maximun
        self.focus_gotomax_button = QtGui.QPushButton('go to maximun')
        self.focus_gotomax_button.setCheckable(False)
        self.focus_gotomax_button.clicked.connect(self.paramChangedInitialize)

        self.focus_gotomax_button.clicked.connect(self.focus_go_to_maximun)
        self.focus_gotomax_button.setToolTip('guarda el patron en el z actual')

    # En otra grid poner las cosas del foco
        self.grid_focus = QtGui.QWidget()
        grid_focus_layout = QtGui.QGridLayout()
        self.grid_focus.setLayout(grid_focus_layout)
        grid_focus_layout.addWidget(self.focus_lock_button,       1, 1, 2, 1)
        grid_focus_layout.addWidget(self.focus_autocorr_button,   2, 1, 2, 1)
        grid_focus_layout.addWidget(self.focus_gotomax_button,    3, 1, 2, 1)
        grid_focus_layout.addWidget(focus_laser_label,            2, 2)
        grid_focus_layout.addWidget(self.focus_laser,             3, 2)

    # particles to autofocus
        self.autofocLabel = QtGui.QLabel('Particles after autofocus')
        self.autofocEdit = QtGui.QLineEdit('10')
        self.autofocEdit.setFixedWidth(40)
        self.autofocEdit.setToolTip('Cantida de impresiones hasta autofoquear')

    # shift x
        self.shifxLabel = QtGui.QLabel('focus shift X [µm]')
        self.shiftxEdit = QtGui.QLineEdit('10')
        self.shiftxEdit.setFixedWidth(40)
        self.shiftxEdit.setToolTip('Para que haga el autofoco corrido ')

    # shift y
        self.shiftyLabel = QtGui.QLabel('focus shift Y [µm]')
        self.shiftyEdit = QtGui.QLineEdit('10')
        self.shiftyEdit.setFixedWidth(40)
        self.shiftyEdit.setToolTip('Para que haga el autofoco corrido ')

    # En otra grid poner las cosas del foco
        self.grid_shift = QtGui.QWidget()
        grid_shift_layout = QtGui.QGridLayout()
        self.grid_shift.setLayout(grid_shift_layout)
        grid_shift_layout.addWidget(self.autofocLabel, 1, 0)
        grid_shift_layout.addWidget(self.autofocEdit,  2, 0)
        grid_shift_layout.addWidget(self.shifxLabel,   3, 0)
        grid_shift_layout.addWidget(self.shiftxEdit,   4, 0)
        grid_shift_layout.addWidget(self.shiftyLabel,  5, 0)
        grid_shift_layout.addWidget(self.shiftyEdit,   6, 0)

    # separo tambien los shutters y flipper

    # Shutters buttons
        self.shutter0button = QtGui.QCheckBox('shutter Green')
        self.shutter0button.clicked.connect(self.shutter0)
        self.shutter0button.setStyleSheet("color: green; ")

        self.shutter1button = QtGui.QCheckBox('shutter Red')
        self.shutter1button.clicked.connect(self.shutter1)
        self.shutter1button.setStyleSheet("color: red; ")

        self.shutter2button = QtGui.QCheckBox('shutter Blue')
        self.shutter2button.clicked.connect(self.shutter2)
        self.shutter2button.setStyleSheet("color: blue; ")

        self.shutter3button = QtGui.QCheckBox('shutter IR (808)')
        self.shutter3button.clicked.connect(self.shutter3)
        self.shutter3button.setStyleSheet("color: dark red; ")

#        self.shutter3button.clicked.connect(lambda: self.openShutter(shutter[3]))


        self.shutter0button.setToolTip('Open/close Green 532 Shutter')
        self.shutter1button.setToolTip('Open/close red 640 Shutter')
        self.shutter2button.setToolTip('Open/close blue 405 Shutter')
        self.shutter3button.setToolTip('Open/close IR 808 Shutter')

        self.power_check = QtGui.QCheckBox('Potencia')
#        self.power_check.setChecked(False)  # TODO: No esta conectado al flipper.
#        self.power_check.clicked.connect(self.flipper0/1) # funcion flipper?
        self.power_check.clicked.connect(self.power_change)
        self.power_check.setToolTip('Picado es baja, no picado es alta')
        self.power_change()

        self.grid_shutters = QtGui.QWidget()
        grid_shutters_layout = QtGui.QGridLayout()
        self.grid_shutters.setLayout(grid_shutters_layout)
        grid_shutters_layout.addWidget(self.shutter0button,        0, 1)
        grid_shutters_layout.addWidget(self.shutter1button,        1, 1)
        grid_shutters_layout.addWidget(self.shutter2button,        2, 1)
        grid_shutters_layout.addWidget(self.shutter3button,        3, 1)

        grid_shutters_layout.addWidget(self.power_check,           1, 2, 1, 2)

    # boton de dimeros
        self.dimeros_button = QtGui.QPushButton("DIMEROS")
        self.dimeros_button.setCheckable(False)
#        self.dimeros_button.clicked.connect(self.algo1)
        self.dimeros_button.setToolTip('no se que hace')

    # Go to maximun
        self.dimeros_next_button = QtGui.QPushButton("Next Dimer")
        self.dimeros_next_button.setCheckable(False)
#        self.dimeros_button.clicked.connect(self.algo2)
        self.dimeros_next_button.setToolTip('empieza')

    # tiempo de espera dimeros
        self.t_waitLabel = QtGui.QLabel('t espera (s)')
        self.t_waitEdit = QtGui.QLineEdit('60')
        self.t_waitEdit.setFixedWidth(40)
        self.t_waitEdit.setToolTip('Tiempo que mantiene el laser prendido.')
        self.t_waitLabel.setToolTip('Tiempo que mantiene el laser prendido.')

    # Defino el tipo de laser que quiero para imprimir
        self.preescan_laser = QtGui.QComboBox()
        self.preescan_laser.addItems(shutters)
        self.preescan_laser.setCurrentIndex(1)
        self.preescan_laser.setToolTip('Elijo el shuter para Preescanear el que ya está')
        self.preescan_laser.setFixedWidth(80)
        self.preescan_laser.activated.connect(
                                lambda: self.color_menu(self.preescan_laser))
        self.color_menu(self.preescan_laser)

    # Defino el tipo de laser que quiero para imprimir
        self.dimerscan_laser = QtGui.QComboBox()
        self.dimerscan_laser.addItems(shutters)
        self.dimerscan_laser.setCurrentIndex(2)
        self.dimerscan_laser.setToolTip('Elijo el shuter para escanear el dimero ')
        self.dimerscan_laser.setFixedWidth(80)
        self.dimerscan_laser.activated.connect(
                                lambda: self.color_menu(self.dimerscan_laser))
        self.color_menu(self.dimerscan_laser)

    # particulas totales
        self.dimero_totalLabel = QtGui.QLabel('Dimeros totales')
        self.dimero_totalEdit = QtGui.QLabel('0')
        self.dimero_totalEdit.setFixedWidth(40)
        self.dimero_totalEdit.setToolTip('Cantidad de particulas totales a imprimir')
    # Indice actual
        self.indice_dimeroLabel = QtGui.QLabel('Indice dimero')
        self.indice_dimeroEdit = QtGui.QLabel('0')
        self.indice_dimeroEdit.setFixedWidth(40)
        self.indice_dimeroEdit.setStyleSheet(
                                        " background-color: rgb(200,200,200)")

    # Posicion a imprimir el dimero
        self.dimero_posxLabel = QtGui.QLabel('Dx [µm]')
        self.dimero_posxEdit = QtGui.QLineEdit('10')
        self.dimero_posxEdit.setFixedWidth(40)
        self.dimero_posxEdit.setToolTip('distancia en x donde imprimir.')
        self.dimero_posyLabel = QtGui.QLabel('Dy [µm]')
        self.dimero_posyEdit = QtGui.QLineEdit('0')
        self.dimero_posyEdit.setFixedWidth(40)
        self.dimero_posyEdit.setToolTip('distancia en y donde imprimir')

    # En otra grid poner las cosas de crecimiento/Dimeros
        self.grid_grow = QtGui.QWidget()

        grid_grow = QtGui.QGridLayout()
        self.grid_grow.setLayout(grid_grow)
        grid_grow.addWidget(self.dimeros_button,       1, 0)
        grid_grow.addWidget(self.dimeros_next_button,  1, 1)
        grid_grow.addWidget(self.t_waitLabel,          4, 1)
        grid_grow.addWidget(self.t_waitEdit,           5, 1)

        grid_grow.addWidget(self.dimero_posxLabel,     2, 1)
        grid_grow.addWidget(self.dimero_posxEdit,      3, 1)
        grid_grow.addWidget(self.dimero_posyLabel,     2, 2)
        grid_grow.addWidget(self.dimero_posyEdit,      3, 2)
        
        grid_grow.addWidget(QtGui.QLabel('Pre scan Laser'),   4, 0)
        grid_grow.addWidget(QtGui.QLabel('Dimer scan Laser'),  4, 4)
        grid_grow.addWidget(self.preescan_laser,   5, 0)
        grid_grow.addWidget(self.dimerscan_laser,  5, 4)
        grid_grow.addWidget(self.indice_dimeroLabel,             1, 4)
        grid_grow.addWidget(self.indice_dimeroEdit,              2, 4)

        grid_grow.addWidget(QtGui.QLabel(''),          2, 0)
        grid_grow.addWidget(QtGui.QLabel(''),          6, 0)

    # Read pos button.
        self.read_pos_button = QtGui.QPushButton("Read")
        self.read_pos_button.setCheckable(False)
        self.read_pos_button.clicked.connect(self.read_pos)
        self.read_pos_button.setToolTip('Lee la posicion actual')
        self.read_pos_Label = QtGui.QLabel('Posicion medida')

    # Valores de refecencia
        self.xrefLabel = QtGui.QLabel('80')
        self.yrefLabel = QtGui.QLabel('80')
        self.zrefLabel = QtGui.QLabel('80')

        self.grid_reference = QtGui.QWidget()
        grid_reference = QtGui.QGridLayout()
        self.grid_reference.setLayout(grid_reference)
        grid_reference.addWidget(QtGui.QLabel(''),          0, 0)
        grid_reference.addWidget(QtGui.QLabel(''),          4, 0)
        grid_reference.addWidget(QtGui.QLabel(''),          5, 0)
        grid_reference.addWidget(self.xrefLabel,            1, 1)
        grid_reference.addWidget(self.yrefLabel,            2, 1)
        grid_reference.addWidget(self.zrefLabel,            3, 1)
        grid_reference.addWidget(QtGui.QLabel('x ref ='),   1, 0)
        grid_reference.addWidget(QtGui.QLabel('y ref ='),   2, 0)
        grid_reference.addWidget(QtGui.QLabel('z ref ='),   3, 0)

# --- FIN COSAS RUTINARIAS PRINTING

        imageWidget = pg.GraphicsLayoutWidget()
        self.vb = imageWidget.addViewBox(row=1, col=1)

        # estos point_graph son para marcar en el Viebox del scan
        self.point_graph_Gauss = pg.ScatterPlotItem(size=10,
                                                    symbol='o', color='m')
        self.point_graph_CM = pg.ScatterPlotItem(size=10,
                                                 symbol='+', color='m')

    # LiveView Button
        self.liveviewButton = QtGui.QPushButton('confocal Scan')
        self.liveviewButton.setCheckable(True)
        self.liveviewButton.clicked.connect(self.liveview)
        self.liveviewButton.setStyleSheet(
                "QPushButton { background-color: green; }"
                "QPushButton:pressed { background-color: blue; }")
        self.liveviewButton.setToolTip('The magic begins (scan)')

#        self.PSFMode = QtGui.QComboBox()  # TODO: AGREGAR XZ, YZ
#        self.PSFModes = ['XY normal psf', 'XZ', 'YZ']
#        self.PSFMode.addItems(self.PSFModes)
#        self.PSFMode.activated.connect(self.PSFYZ)
#        self.PSFMode.setToolTip('Change the scan axes')

    # To save every image scaned
        self.VideoCheck = QtGui.QCheckBox('"video" save')
        self.VideoCheck.setChecked(False)
        self.VideoCheck.setToolTip('Save every finished image')

    # to run continuously
        self.Continouscheck = QtGui.QCheckBox('Continous')
        self.Continouscheck.setChecked(False)
        self.Continouscheck.setToolTip('Start again, and again, and again...')

    # to Calculate the mass center
        self.CMcheck = QtGui.QCheckBox('calcula CM')
        self.CMcheck.setCheckable(False)
        self.CMcheck.clicked.connect(self.CMmeasure)
        self.CMcheck.setToolTip('makes a basic measurement of\
                                the center of mass')

    # 2D Gaussian fit to estimate the center of a NP
        self.Gausscheck = QtGui.QCheckBox('Gauss fit')
        self.Gausscheck.setCheckable(False)
        self.Gausscheck.clicked.connect(self.GaussFit)
        self.Gausscheck.setToolTip('makes 2D Gaussian fit of the image,\
                                   and give the center')

    # save image Button
        self.saveimageButton = QtGui.QPushButton('Save Frame')
        self.saveimageButton.setCheckable(False)
        self.saveimageButton.clicked.connect(self.saveFrame)
        self.saveimageButton.setStyleSheet(
                "QPushButton { background-color:  rgb(200, 200, 10); }"
                "QPushButton:pressed { background-color: blue; }")

        label_save = QtGui.QLabel('Tiff File Name')
        label_save.resize(label_save.sizeHint())
        self.edit_save = QtGui.QLineEdit('Test Image')
        self.edit_save.resize(self.edit_save.sizeHint())
        self.edit_save.setToolTip('Selec a name to save the image.\
              The name automatically changes to not replace the previous one')

        self.edit_Name = str(self.edit_save.text())
        self.edit_save.textEdited.connect(self.save_name_update)
        self.save_name_update()
        tamaño = 110
        self.edit_save.setFixedWidth(tamaño)
        self.saveimageButton.setFixedWidth(tamaño)

        self.NameDirValue = QtGui.QLabel('')
        self.NameDirValue.setText(self.main.file_path)
        self.NameDirValue.setStyleSheet(" background-color: red; ")

    # Select the wanted scan mode
        self.scanMode = QtGui.QComboBox()
        self.scanMode.addItems(scanModes)  # step or ramp
        self.scanMode.setToolTip('Selec the scan type.\
        With a voltage ramps or step by step')

    # Change between Fwd & Bwd
        self.imagecheck = QtGui.QCheckBox('Image change')
        self.imagecheck.clicked.connect(self.imageplot)
        self.imagecheck.setStyleSheet(" color: red; ")
        self.imagecheck.setToolTip('Switch between the images FWd and BWD')

    # useful Booleans
        self.channelramp = False  # canales
        self.channelsteps = False
        self.shuttering = False
        self.autoLevels = True
        self.YZ = False
        self.GaussPlot = False
        self.CMplot = False
        self.locked_focus = False  # when the focus is locked, it get True condition
#        self.shuttersignal = [False]*len(shutters)  # el printing esta al revez
        self.shuttersignal = [True]*len(shutters)


    # autoLevel image. Change between automatic colorScale or manual
        self.autoLevelscheck = QtGui.QCheckBox('Auto escale (or not)')
        self.autoLevelscheck.setChecked(True)
        self.autoLevelscheck.clicked.connect(self.autoLevelset)
        self.autoLevelscheck.setToolTip('Switch between automatic \
                                        colorbar normalization, or manually')

    # ploting image with matplotlib (slow). if Npix>500 is very slow
        self.plotLivebutton = QtGui.QPushButton('Plot this frame')
        self.plotLivebutton.setChecked(False)
        self.plotLivebutton.clicked.connect(self.plotLive)
        self.plotLivebutton.setToolTip('Plot this image with matplotlive')

    # Select the detector
        self.detectMode = QtGui.QComboBox()
        self.detectMode.addItems(detectModes)  # only PD. not ussefull anymore
        self.detectMode.setToolTip('Select the detect instrument (APD or PMT)')

    # Point scan (TRAZA)
        self.trazaButton = QtGui.QPushButton('TRAZA')
        self.trazaButton.setCheckable(False)
        self.trazaButton.clicked.connect(self.traza_start)
        self.trazaLabel = QtGui.QLabel('<strong>0.00|0.00')
        self.trazaButton.setToolTip('continuously measures the APDs (Ctrl+T)')

    # Scanning parameters

        self.scanRangeEdit = QtGui.QLineEdit('2')
        self.pixelTimeEdit = QtGui.QLineEdit('1')
        self.pixelTimeEdit.setToolTip('0.01 ms = 10 µs  :)')
        self.numberofPixelsEdit = QtGui.QLineEdit('32')
        self.pixelSizeValue = QtGui.QLineEdit('20')

        self.timeTotalLabel = QtGui.QLabel('total scan time (s)')
        self.timeTotalLabel.setToolTip('Is an aproximate value')

        self.onlyInt = QtGui.QIntValidator(0, 10001)
        self.numberofPixelsEdit.setValidator(self.onlyInt)
        self.onlypos = QtGui.QDoubleValidator(0, 1000, 10)
        self.pixelTimeEdit.setValidator(self.onlypos)
        self.scanRangeEdit.setValidator(self.onlypos)

        self.numberofPixelsEdit.textEdited.connect(self.PixelSizeChange)
        self.pixelSizeValue.textEdited.connect(self.NpixChange)
        self.scanRangeEdit.textEdited.connect(self.PixelSizeChange)

    # Defino el tipo de laser que quiero para imprimir
        self.scan_laser = QtGui.QComboBox()
        self.scan_laser.addItems(shutters)
        self.scan_laser.setCurrentIndex(2)
        self.scan_laser.setToolTip('Elijo el shuter para scanear')
        self.scan_laser.setFixedWidth(80)
        self.scan_laser.activated.connect(
                                    lambda: self.color_menu(self.scan_laser))
        self.color_menu(self.scan_laser)
        scan_laser = QtGui.QLabel('<strong> Scan Laser')

    # Defino el tipo de laser que quiero para imprimir
        self.traza_laser = QtGui.QComboBox()
        self.traza_laser.addItems(shutters)
        self.traza_laser.setCurrentIndex(2)
        self.traza_laser.setToolTip('Elijo el shuter para las trazas')
        self.traza_laser.setFixedWidth(80)
        self.traza_laser.activated.connect(
                                    lambda: self.color_menu(self.traza_laser))
        self.color_menu(self.traza_laser)
        traza_laser = QtGui.QLabel('<strong> Trazas Laser')

        self.paramWidget = QtGui.QWidget()

        subgrid = QtGui.QGridLayout()
        self.paramWidget.setLayout(subgrid)

        self.paramWidget2 = QtGui.QWidget()
        subgrid2 = QtGui.QGridLayout()
        self.paramWidget2.setLayout(subgrid2)

        self.paramWidget3 = QtGui.QWidget()
        subgrid3 = QtGui.QGridLayout()
        self.paramWidget3.setLayout(subgrid3)

    # Columna 1
        subgrid.addWidget(scan_laser,               0, 1)
        subgrid.addWidget(self.scan_laser,          1, 1)
        subgrid.addWidget(QtGui.QLabel('      '),   2, 1)
        subgrid.addWidget(QtGui.QLabel('Scan range (µm)'),      3, 1)
        subgrid.addWidget(self.scanRangeEdit,       4, 1)
        subgrid.addWidget(QtGui.QLabel('Pixel time (ms)'),      5, 1)
        subgrid.addWidget(self.pixelTimeEdit,       6, 1)
        subgrid.addWidget(QtGui.QLabel('Number of pixels') ,    7, 1)
        subgrid.addWidget(self.numberofPixelsEdit,  8, 1)
        subgrid.addWidget(QtGui.QLabel('Pixel size (nm)'),      9, 1)
        subgrid.addWidget(self.pixelSizeValue,     10, 1)
        subgrid.addWidget(self.liveviewButton,     11, 1)
        subgrid.addWidget(self.Continouscheck,     12, 1)
        subgrid.addWidget(self.autoLevelscheck,    13, 1)
        subgrid.addWidget(self.imagecheck,         14, 1)

    # Columna 2

        subgrid2.addWidget(traza_laser,              0, 2)
        subgrid2.addWidget(self.traza_laser,         1, 2)
        subgrid2.addWidget(self.trazaButton,         2, 2)
        subgrid2.addWidget(self.trazaLabel,          3, 2)
        subgrid2.addWidget(self.detectMode,          4, 2)
        subgrid2.addWidget(QtGui.QLabel(""),         5, 2)
        subgrid2.addWidget(QtGui.QLabel("x/y scan"),   6, 2)
        subgrid2.addWidget(QtGui.QLabel("x/z scan"),   7, 2)
        subgrid2.addWidget(QtGui.QLabel("z/y scan"),   8, 2)
        subgrid2.addWidget(self.VideoCheck,          9, 2)
        subgrid2.addWidget(QtGui.QLabel(""),        10, 2)
        subgrid2.addWidget(label_save,              11, 2)
        subgrid2.addWidget(self.edit_save,          12, 2)
        subgrid2.addWidget(self.saveimageButton,    13, 2)
        subgrid2.addWidget(QtGui.QLabel(""),        14, 2)

        subgrid2.addWidget(self.timeTotalLabel,     16, 2)


    # Columna 3
        subgrid3.addWidget(QtGui.QLabel(""),          0, 3)

        subgrid3.addWidget(QtGui.QLabel(""),          2, 3)

        subgrid3.addWidget(QtGui.QLabel(""),          5, 3)

        subgrid3.addWidget(QtGui.QLabel(""),          7, 3)
        subgrid3.addWidget(QtGui.QLabel(""),          8, 3)

        subgrid3.addWidget(QtGui.QLabel(""),         11, 3)

        subgrid3.addWidget(self.plotLivebutton,      13, 3)
        subgrid3.addWidget(QtGui.QLabel(""),         14, 3)
        subgrid3.addWidget(self.scanMode,            15, 3)
#        subgrid3.addWidget(self.PSFMode,             16, 3)

# ---  Positioner part ---------------------------------
        # Axes control
        self.StepEdit = QtGui.QLineEdit("0.1")

        self.xLabel = QtGui.QLabel('0.0')
        self.xLabel.setTextFormat(QtCore.Qt.RichText)
        self.xname = QtGui.QLabel("<strong>x =")
        self.xname.setTextFormat(QtCore.Qt.RichText)
        self.xUpButton = QtGui.QPushButton("(+x) ►")  # →
        self.xUpButton.pressed.connect(
                       lambda: self.move("x", float(self.StepEdit.text())))
        self.xDownButton = QtGui.QPushButton("◄ (-x)")  # ←
        self.xDownButton.pressed.connect(
                       lambda: self.move("x", -float(self.StepEdit.text())))
        self.xUp2Button = QtGui.QPushButton("► x ►")  # →
        self.xUp2Button.pressed.connect(
                       lambda: self.move("x", 10*float(self.StepEdit.text())))
        self.xDown2Button = QtGui.QPushButton("◄ x ◄")  # ←
        self.xDown2Button.pressed.connect(
                       lambda: self.move("x", -10*float(self.StepEdit.text())))

        self.yLabel = QtGui.QLabel('0.0')
        self.yLabel.setTextFormat(QtCore.Qt.RichText)
        self.yname = QtGui.QLabel("<strong>y =")
        self.yname.setTextFormat(QtCore.Qt.RichText)
        self.yUpButton = QtGui.QPushButton("(+y) ▲")  # ↑
        self.yUpButton.pressed.connect(
                       lambda: self.move("y", float(self.StepEdit.text())))
        self.yDownButton = QtGui.QPushButton("(-y) ▼")  # ↓
        self.yDownButton.pressed.connect(
                       lambda: self.move("y", -float(self.StepEdit.text())))
        self.yUp2Button = QtGui.QPushButton("▲ y ▲")  # ↑
        self.yUp2Button.pressed.connect(
                       lambda: self.move("y", 10*float(self.StepEdit.text())))
        self.yDown2Button = QtGui.QPushButton("▼ y ▼")  # ↓
        self.yDown2Button.pressed.connect(
                       lambda: self.move("y", -10*float(self.StepEdit.text())))

        self.zStepEdit = QtGui.QLineEdit("0.1")

        self.zLabel = QtGui.QLabel('10.0')
        self.zLabel.setTextFormat(QtCore.Qt.RichText)
        self.zname = QtGui.QLabel("<strong>z =")
        self.zname.setTextFormat(QtCore.Qt.RichText)
        self.zUpButton = QtGui.QPushButton("+z ▲")
        self.zUpButton.pressed.connect(
                       lambda: self.zMoveUp())
        self.zDownButton = QtGui.QPushButton("-z ▼")
        self.zDownButton.pressed.connect(
                       lambda: self.zMoveDown())
        self.zup2Button = QtGui.QPushButton("▲ z ▲")
        self.zup2Button.pressed.connect(
                       lambda: self.zMoveUp(10))
        self.zDown2Button = QtGui.QPushButton("▼ z ▼")
        self.zDown2Button.pressed.connect(
                       lambda: self.zMoveDown(10))

        tamaño = 40
        self.xLabel.setFixedWidth(tamaño)
        self.yLabel.setFixedWidth(tamaño)
        self.zLabel.setFixedWidth(tamaño)
        tamaño = 50
        self.xUp2Button.setFixedWidth(tamaño)
        self.xDown2Button.setFixedWidth(tamaño)
        self.xUpButton.setFixedWidth(tamaño)
        self.xDownButton.setFixedWidth(tamaño)
        self.yUp2Button.setFixedWidth(tamaño)
        self.yDown2Button.setFixedWidth(tamaño)
        self.yUpButton.setFixedWidth(tamaño)
        self.yDownButton.setFixedWidth(tamaño)

        self.positioner = QtGui.QWidget()

        layout = QtGui.QGridLayout()
        self.positioner.setLayout(layout)
        layout.addWidget(self.xname,        1, 0)
        layout.addWidget(self.xLabel,       1, 1)
        layout.addWidget(self.xUpButton,    2, 6, 2, 1)
        layout.addWidget(self.xDownButton,  2, 4, 2, 1)
        layout.addWidget(self.xUp2Button,   2, 7, 2, 1)
        layout.addWidget(self.xDown2Button, 2, 3, 2, 1)

        layout.addWidget(self.yname,       2, 0)
        layout.addWidget(self.yLabel,      2, 1)
        layout.addWidget(self.yUpButton,   1, 5, 3, 1)
        layout.addWidget(self.yDownButton, 3, 5, 2, 1)
        layout.addWidget(QtGui.QLabel("step x/y [µm] "), 4, 6, 1, 2)
        layout.addWidget(self.StepEdit,   5, 6)
        layout.addWidget(self.yUp2Button,   0, 5, 2, 1)
        layout.addWidget(self.yDown2Button, 4, 5, 2, 1)

        layout.addWidget(self.zname,       4, 0)
        layout.addWidget(self.zLabel,      4, 1)
        layout.addWidget(self.zup2Button,   0, 9, 2, 1)
        layout.addWidget(self.zUpButton,   1, 9, 3, 1)
        layout.addWidget(self.zDownButton, 3, 9, 2, 1)
        layout.addWidget(self.zDown2Button, 4, 9, 2, 1)
        layout.addWidget(QtGui.QLabel("step z [µm] "), 4, 10)
        layout.addWidget(self.zStepEdit,   5, 10)

        layout.addWidget(self.NameDirValue, 8, 0, 1, 7)
        layout.addWidget(self.read_pos_button, 0, 0, 1, 2)

        tamaño = 40
        self.StepEdit.setFixedWidth(tamaño)
        self.zStepEdit.setFixedWidth(tamaño)

        layout.addWidget(QtGui.QLabel("|"),  1, 2)
        layout.addWidget(QtGui.QLabel("|"),  2, 2)
        layout.addWidget(QtGui.QLabel("|"),  3, 2)
        layout.addWidget(QtGui.QLabel("|"),  4, 2)
        layout.addWidget(QtGui.QLabel("|"),  5, 2)

        layout.addWidget(QtGui.QLabel("|"),  1, 8)
        layout.addWidget(QtGui.QLabel("|"),  2, 8)
        layout.addWidget(QtGui.QLabel("|"),  3, 8)
        layout.addWidget(QtGui.QLabel("|"),  4, 8)
        layout.addWidget(QtGui.QLabel("|"),  5, 8)

        self.gotoWidget = QtGui.QWidget()
        layout2 = QtGui.QGridLayout()
        self.gotoWidget.setLayout(layout2)
        layout2.addWidget(QtGui.QLabel("X [µm]"), 1, 1)
        layout2.addWidget(QtGui.QLabel("Y [µm]"), 2, 1)
        layout2.addWidget(QtGui.QLabel("Z [µm]"), 3, 1)
        self.xgotoLabel = QtGui.QLineEdit("40.000")
        self.ygotoLabel = QtGui.QLineEdit("40.000")
        self.zgotoLabel = QtGui.QLineEdit("40.000")
        self.gotoButton = QtGui.QPushButton("♫ G0 To ♪")
        self.gotoButton.pressed.connect(self.goto)
        layout2.addWidget(self.gotoButton, 1, 5, 2, 2)
        layout2.addWidget(self.xgotoLabel, 1, 2)
        layout2.addWidget(self.ygotoLabel, 2, 2)
        layout2.addWidget(self.zgotoLabel, 3, 2)
        self.zgotoLabel.setValidator(self.onlypos)
        tamaño = 50
        self.xgotoLabel.setFixedWidth(tamaño)
        self.ygotoLabel.setFixedWidth(tamaño)
        self.zgotoLabel.setFixedWidth(tamaño)

        layout3 = QtGui.QGridLayout()
        self.goCMWidget = QtGui.QWidget()
        self.goCMWidget.setLayout(layout3)
        self.CMxValue = QtGui.QLabel('NaN')
        self.CMyValue = QtGui.QLabel('NaN')
        layout3.addWidget(QtGui.QLabel('CM X'), 3, 1)
        layout3.addWidget(self.CMxValue, 4, 1)
        layout3.addWidget(QtGui.QLabel('CM Y'), 3, 2)
        layout3.addWidget(self.CMyValue, 4, 2)
        self.goCMButton = QtGui.QPushButton("♠ Go CM ♣")
        self.goCMButton.pressed.connect(self.goCM)
        layout3.addWidget(self.goCMButton, 1, 4, 1, 2)
        layout3.addWidget(self.CMcheck, 1, 1, 1, 2)
        
        self.GaussxValue = QtGui.QLabel('NaN')
        self.GaussyValue = QtGui.QLabel('NaN')
        layout3.addWidget(QtGui.QLabel('Gauss X'), 3, 4)
        layout3.addWidget(self.GaussxValue, 4, 4)
        layout3.addWidget(QtGui.QLabel('Gauss Y'), 3, 5)
        layout3.addWidget(self.GaussyValue, 4, 5)
#        layout3.addWidget(QtGui.QLabel(' '), 4, 4)
        self.goCMButton = QtGui.QPushButton("♥ Go Gauss ♦")
        self.goCMButton.pressed.connect(self.goGauss)
        layout3.addWidget(self.goCMButton, 2, 4, 1, 2)
        layout3.addWidget(self.Gausscheck, 2, 1, 1, 2)

# ---- fin positioner part----------


# ----DOCK cosas, mas comodo!
        self.state = None  # defines the docks state (personalize your oun UI!)
        hbox = QtGui.QHBoxLayout(self)
        dockArea = DockArea()

        viewDock = Dock('viewbox', size=(50, 45))
        viewDock.addWidget(imageWidget)
        viewDock.hideTitleBar()
        dockArea.addDock(viewDock, 'left')

        scanDock = Dock('Scan parameters', size=(1, 1))
        scanDock.addWidget(self.paramWidget)
        dockArea.addDock(scanDock, 'right', viewDock)

        self.otrosDock = Dock('Other things', size=(1, 1))
    # era para cosas de roi que saque. Pero puede usarse para otra cosa.
        dockArea.addDock(self.otrosDock, 'bottom')

        posDock = Dock('positioner', size=(1, 1))
        posDock.addWidget(self.positioner)
        dockArea.addDock(posDock, 'above', self.otrosDock)

        goCMDock = Dock('Cm and Gauss', size=(1, 1))
        goCMDock.addWidget(self.goCMWidget)
        dockArea.addDock(goCMDock, 'right', posDock)

        gotoDock = Dock('goto', size=(1, 1))
        gotoDock.addWidget(self.gotoWidget)
        dockArea.addDock(gotoDock, 'above', goCMDock)

        scanDock3 = Dock('ROI Things', size=(1, 1))
        scanDock3.addWidget(self.paramWidget3)
        dockArea.addDock(scanDock3, 'right')

        scanDock2 = Dock('Other parameters', size=(1, 1))
        scanDock2.addWidget(self.paramWidget2)
        dockArea.addDock(scanDock2, 'left', scanDock3)

        grid_print_dock = Dock('Printing grids', size=(5, 10))
        grid_print_dock.addWidget(self.grid_print)
        dockArea.addDock(grid_print_dock, 'bottom')

        grid_focus_dock = Dock('Focus cosas', size=(1, 1))
        grid_focus_dock.addWidget(self.grid_focus)
        dockArea.addDock(grid_focus_dock, 'bottom', scanDock2)

        grid_shift_dock = Dock('Focus shift', size=(1, 1))
        grid_shift_dock.addWidget(self.grid_shift)
        dockArea.addDock(grid_shift_dock, 'right', grid_print_dock)

        shutters_dock = Dock('Shutters', size=(1, 1))
        shutters_dock.addWidget(self.grid_shutters)
        dockArea.addDock(shutters_dock, 'bottom', scanDock3)

        grow_dock = Dock('Dimeros/Crecimiento', size=(1, 1))
        grow_dock.addWidget(self.grid_grow)
        dockArea.addDock(grow_dock, 'right', grid_shift_dock)

        grid_reference_Dock = Dock('Reference pos', size=(1, 1))
        grid_reference_Dock.addWidget(self.grid_reference)
        dockArea.addDock(grid_reference_Dock, 'left', posDock)


        hbox.addWidget(dockArea)
        self.setLayout(hbox)

# FIN botones# FIN botones# FIN botones
        # FIN botones# FIN botones# FIN botones# FIN botones
        # FIN botones# FIN botones# FIN botones# FIN botones
        # FIN botones# FIN botones# FIN botones# FIN botones

    #  algunas cosas que ejecutan una vez antes de empezar
        self.shuttersChannelsNidaq()  # open a digital channel and let it open

        self.read_pos()  # read where it is and write in the x/y/zLabel texts

        self.paramChanged()
        self.PixelSizeChange()

        self.vb.setMouseMode(pg.ViewBox.RectMode)
        self.img = pg.ImageItem()
        self.img.translate(-0.5, -0.5)
        self.vb.addItem(self.img)
        self.vb.setAspectLocked(True)
        imageWidget.setAspectLocked(True)
        self.hist = pg.HistogramLUTItem(image=self.img)
        self.hist.gradient.loadPreset('thermal')
# 'thermal', 'flame', 'yellowy', 'bipolar', 'spectrum',
# 'cyclic', 'greyclip', 'grey' # Solo son estos
        self.hist.vb.setLimits(yMin=0, yMax=66000)

        for tick in self.hist.gradient.ticks:
            tick.hide()
        imageWidget.addItem(self.hist, row=1, col=2)

        self.PDtimer = QtCore.QTimer()
        self.PDtimer.timeout.connect(self.rampupdate)

        self.steptimer = QtCore.QTimer()
        self.steptimer.timeout.connect(self.stepupdate)

        self.dy = 0

        self.dockArea = dockArea  # lo paso a self. por si lo usaba despues

# %% shortcuts todos juntos
        self.liveviewAction = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+a'), self, self.liveviewKey)

        self.grid_start_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F5'), self, self.grid_start)

        self.focus_maximun_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F8'), self, self.focus_go_to_maximun)

        self.grid_read_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F1'), self, self.grid_read)

        self.grid_autocorr_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F9'), self, self.focus_autocorr_rampas)

        self.lock_focus_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('ctrl+f'), self, self.focus_lock_focus_rampas)

        self.lock_focus_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('ctrl+t'), self, self.traza_start)
#TODO: agregar mas Shortcuts copados (o copiar los de labview)

# %% Un monton de pequeñas cosas funciones que agregé
    def imageplot(self):
        if self.imagecheck.isChecked():
            self.img.setImage(self.image2, autoLevels=self.autoLevels)
            self.imagecheck.setStyleSheet(" color: green; ")
        else:
            self.img.setImage(self.image, autoLevels=self.autoLevels)
            self.imagecheck.setStyleSheet(" color: red; ")

    def liveviewKey(self):
        '''Triggered by the liveview shortcut.'''
        if self.liveviewButton.isChecked():
            self.liveviewStop()
            self.liveviewButton.setChecked(False)
        else:
            self.liveviewButton.setChecked(True)
            self.liveview()

    def autoLevelset(self):
        """config the auto normalize of the scan colorbar"""
        if self.autoLevelscheck.isChecked():
            self.autoLevels = True
        else:
            self.autoLevels = False

#    def PSFYZ(self):  era para el YZ, XZ
#        if self.PSFMode.currentText() == self.PSFModes[0]:
#            self.YZ = False
#        else:
#            self.YZ = True

    def zeroImage(self):
        """creates two empty image Fwd and Bwd"""
        self.blankImage = np.zeros((self.numberofPixels, self.numberofPixels))
        self.image = np.copy(self.blankImage)
        self.image2 = np.copy(self.blankImage)

    def PixelSizeChange(self):
        """Automaticaly sets the correct pixelSize when the numer of pix change """
        scanRange = float(self.scanRangeEdit.text())
        numberofPixels = int(self.numberofPixelsEdit.text())
        self.pixelSize = scanRange/numberofPixels
        self.pixelSizeValue.setText('{}'.format(
                                    np.around(1000 * self.pixelSize, 2)))
        pixelTime = float(self.pixelTimeEdit.text()) / 10**3
        pixelTime = float(self.pixelTimeEdit.text()) / 10**3
        self.timeTotalLabel.setText("Tiempo total (s) = " + '{}'.format(
                                  np.around(numberofPixels**2 * pixelTime, 2)))

    def NpixChange(self):
        """Automaticaly sets the correct numer of pix when the pixelSize change
        Its round to the closest int"""
        scanRange = float(self.scanRangeEdit.text())
        pixelSize = float(self.pixelSizeValue.text())/1000
        self.numberofPixelsEdit.setText('{}'.format(int(scanRange/pixelSize)))
        pixelTime = float(self.pixelTimeEdit.text()) / 10**3
        self.timeTotalLabel.setText("Tiempo total (s) = " + '{}'.format(
                                np.around(
                                  int(scanRange/pixelSize)**2 * pixelTime, 2)))

# %%--- paramChanged / PARAMCHANGEDinitialize
    def paramChangedInitialize(self):  # TODO: Podria sacarlo...
        """ update de parameters only if something change"""
        tic = ptime.time()

        a = [self.scanRange,
             self.numberofPixels,
             self.pixelTime,
             self.initialPosition,
             self.scanModeSet]

        b = [float(self.scanRangeEdit.text()),
             int(self.numberofPixelsEdit.text()),
             float(self.pixelTimeEdit.text()) / 10**3,
             (float(self.xLabel.text()), float(self.yLabel.text()), float(self.zLabel.text())),
             self.scanMode.currentText()]

#        print("\n", a)
#        print(b, "\n")
        if a != b:
            self.paramChanged()

        toc = ptime.time()
        print("tiempo paramchangeInitailize (ms)", (toc-tic)*10**3, "\n")

    def paramChanged(self):
        tic = ptime.time()

        self.GaussPlot = False
        self.CMplot = False

        self.scanModeSet = self.scanMode.currentText()
#        self.PSFModeSet = self.PSFMode.currentText()

        self.scanRange = float(self.scanRangeEdit.text())
        self.numberofPixels = int(self.numberofPixelsEdit.text())
        self.pixelTime = float(self.pixelTimeEdit.text()) / 10**3  # transform into seconds

        self.initialPosition = (float(self.xLabel.text()),
                                float(self.yLabel.text()),
                                float(self.zLabel.text()))

        self.pixelSize = self.scanRange / self.numberofPixels

        self.pixelSizeValue.setText('{}'.format(np.around(
                                        1000 * self.pixelSize, 2)))  # en nm

        self.linetime = self.pixelTime * self.numberofPixels  # en s

        self.timeTotalLabel.setText("Time total(s) ~ " + '{}'.format(np.around(
                        2 * self.numberofPixels * self.linetime, 2)))

        if self.scanMode.currentText() == scanModes[1]:  # "step scan":
            self.Steps()
        else:  # ramp scan
            self.sampleRate = np.round(1 / self.pixelTime, 9)
            self.Ramps()
#            self.reallinetime = len(self.Npoints) * self.pixelTime  # seconds
            self.PD = np.zeros(self.Npoints)

        self.zeroImage()  # make the blank matriz (image) to fill whit the scan

#        print("\n tiempo paramCahnged (ms)", (ptime.time()-tic)*10**3, "\n")

# %%--- liveview------
# This is the function triggered by pressing the liveview button
    def liveview(self):
        if self.liveviewButton.isChecked():
            # useful print to see when it starts
            print("------------inicio scan---------------------------------------------")
            self.read_pos()  # read the actual position
            self.paramChanged()  # config all the parameters
            self.liveviewStart()  # start the scan rutine
        else:
            self.liveviewStop()

    def liveviewStart(self):
        self.color_scan = self.scan_laser.currentText()  # aca usa el PD del color correcto

        if self.scanMode.currentText() == scanModes[1]:  # "step scan":
            self.channelsOpenStep()  # config de analog in channel for PD's step
            self.tic = ptime.time()
            self.scan_openshutter()  # opens the selected shutter
            self.steptimer.start((self.linetime*10**3))  # imput in ms
        else:  # "ramp scan"
            self.channelsOpenRamp()  # config de analog in channel for PD's ramp
            self.tic = ptime.time()
            self.startingRamps()  # config the PI ramps (piezo platina)
            self.PDtimer.start(self.linetime*10**3)  # imput in ms

    def liveviewStop(self):
#        self.closeShutter(self.color_scan)
        self.closeAllShutters()  # not really necesary
        self.PDtimer.stop()
        pi_device.WGO([1,2,3], [False,False,False])
#        pi_device.StopAll()
        self.MovetoStart()
        self.dy = 0
        self.liveviewButton.setChecked(False)
        self.steptimer.stop()

        self.done()
        self.grid_scan_control = True  # es parte del flujo de grid_start
        print("---------------fin scan--------------------------------------------")

    def scan_openshutter(self):
        """ abre el shutter que se va a utilizar para escanear"""
        for i in range(len(shutters)):
            if self.scan_laser.currentText() == shutters[i]:
                self.openShutter(shutters[i])
                self.scan_shutterabierto = shutters[i]


# %% Starting Ramps
    def startingRamps(self):
        """ Send the signals to the NiDaq, but only start when the trigger is on """

        pi_device.TWC()  # Clear all triggers options

        pi_device.TWS([1,2,3],[1,1,1],[True,True,True])  # config a "High" signal (1) in all channels
        print("Npoints", self.Npoints)
#        pi_device.CTO(1,1,0.005)  # config param 1 (dist for trigger) in 0.005 µm from out 1
        pi_device.CTO(1,3,4)  # The digital output line 1 is set to "Generator Trigger" mode.
        pi_device.CTO(2,3,4)  # The digital output line 2 is set to "Generator Trigger" mode.
        pi_device.CTO(3,3,4)  # The digital output line 3 is set to "Generator Trigger" mode.

#==============================================================================
# #        pi_device.CTO(1,4,5000)  # Trigger delay no anda
#         pi_device.CTO(1,2,1)
#         pi_device.CTO(2,2,1)  # connect the output 2 to the axix 1
#         pi_device.CTO(3,2,1)  # out 3, param 2, valor 1
#         #PERO NO ANDA!!!! en el modelo nuestro (507)
# #TODO: poner bien las cosas del trigger necesarias si las hay
#==============================================================================

        self.PDtask.start()  # empieza despues, con el trigger.

        self.scan_openshutter()  # abre el shutter elegido


#TODO : quizas tambien triggerear el shutter


# %% runing Ramp loop (PD update)
    def rampupdate(self):
        tic = ptime.time()
        
        Npoints = self.Npoints  # int((self.numberofPixels + (self.Nspeed*2))*2)
        Nmedio = int(Npoints/2)

        pi_device.WGO(1, True)
        self.PD = self.PDtask.read(self.Npoints)  # get all points.fw and bw. Need to erase the acelerated zones
        while any(pi_device.IsGeneratorRunning().values()):
            time.sleep(0.1)  # espera a que termine

        pi_device.WGO(1, False)
#        pi_device.MOV('A', self.initialPosition[0])

        imgida = self.PD[PD_channels[self.color_scan]][int(self.Nspeed):int(Nmedio-self.Nspeed)]
        self.image[:, -1-self.dy] = imgida
#        self.img.setImage(self.image, autoLevels=self.autoLevels)

        imgvuelta = self.PD[PD_channels[self.color_scan]][int(Nmedio+self.Nspeed):-int(self.Nspeed)]
        self.image2[:, -1-self.dy] = imgvuelta

        if self.imagecheck.isChecked():
            self.img.setImage(self.image2, autoLevels=self.autoLevels)
        else:
            self.img.setImage(self.image, autoLevels=self.autoLevels)

        pi_device.MOV(['A','B'], [self.initialPosition[0], self.initialPosition[1]+(self.amplitudy*self.dy)])
        while not all(pi_device.qONT().values()):
            # es por si el MOV tarda mucho
            time.sleep(0.01)

#        print(self.dy, "tiempo paso dy", time.time()-tic)

        if self.dy < self.numberofPixels-1:
            self.dy = self.dy + 1
        else:
            self.closeShutter(self.scan_shutterabierto)
            self.PDtimer.stop()
            pi_device.MOV('B', self.initialPosition[1])
    #        self.closeAllShutters()
            if self.VideoCheck.isChecked():
                self.saveFrame()  # para guardar siempre
            print(ptime.time()-self.tic, "Tiempo imagen completa.")
            self.PDtask.stop()
            self.MovetoStart()
            self.dy = 0
            if self.CMcheck.isChecked():
                self.CMmeasure()
                self.goCM()
            if self.Continouscheck.isChecked():
                self.liveviewStart()
            else:
                self.liveviewStop()

# %% --- Creating Ramps  ----
    def Ramps(self):

  # con esto tengo que definir la velocidad en multiplos de 40µs
        if ((self.pixelTime)) / (servo_time) < 1:
            print( "no puede ir tan rapido, se redondeo al mas rapido posible \
            (0.04 (ms) = 40 µs por pixel) Velocidad del servo")

        WTRtime = np.ceil(((self.pixelTime)) / (servo_time))
    # 0.00040(s)*WTRtime*Npoints = (self.pixelTime(s))*Npoints (tiempo rampa)
        self.sampleRate_posta = 1/(WTRtime*servo_time)
#        print(WTRtime, "samplerate", self.sampleRate, self.sampleRate_posta)
        pi_device.WTR(1, WTRtime, 0)
        pi_device.WTR(2, 1, 0)
        nciclos = 1
        pi_device.WGC(1, nciclos)
        pi_device.WGC(2, nciclos)
        pi_device.WOS(1,self.initialPosition[0]) # aditional offset startX
        pi_device.WOS(2,self.initialPosition[1])  # aditional offset startY

        Nspeed = np.ceil(int(self.numberofPixels / 10))
        Npoints = int((self.numberofPixels + (Nspeed*2))*2)
        center = int(Npoints /2)
        amplitudx = self.scanRange
#       tabla, init, Nrampa, appen, center, speed,amplit, offset, lenght
        pi_device.WAV_RAMP(1, 1, Npoints, "X", center,
                           Nspeed, amplitudx, 0, Npoints)

        self.amplitudy = self.scanRange/self.numberofPixels
        self.Npoints = Npoints  # I need these later
        self.Nspeed = Nspeed

# %% --- ChannelsOpen (todos)
# No va mas abrir canales analogicos out para la platina!!!

    def channelsOpenRamp(self):
        """ Open and Config of all the channels for use"""
        if self.channelramp:
            print("ya esta abierto ramp")
        else:
            if self.channelsteps:
                self.done()
            if self.detectMode.currentText() == detectModes[0]:  # 'PD'
                triggerchannelname = "PFI9"
                self.channel_PD_todos(self.sampleRate,
                                      int(self.Npoints*self.numberofPixels),
                                      triggerchannelname)
            self.channelramp = True

    def channelsOpenStep(self):
        """ Open and Config of all the channels for use"""
        if self.channelsteps:
            print("ya esta abierto step")
        else:
            if self.channelramp:
                self.done()
            if self.detectMode.currentText() == detectModes[0]:  # 'PD'
                self.channel_PD_todos()
            self.channelsteps = True

    def channel_PD_todos(self, rate=0, samps_per_chan=0, triggerchannelname=0):
        """ asi tengo todos los PD
        @rate : rate con el que mide el PD
        @samps_per_chan : total de puntos que ve a adquirir en cada canal.\
        Es parecido a Npix*Npix. (como la rampa esta acelerada, es un poquito mas)
        @triggerchannelname : es el nombre del canal por el cual espera el trigger\
        siempre tendria que ser PFI9 o 0 si no quiero trigger."""

        self.PDtask = nidaqmx.Task('PDtask nombre')
        for n in range(len(PDchans)):
            self.PDtask.ai_channels.add_ai_voltage_chan(
                    physical_channel='Dev1/ai{}'.format(PDchans[n]),
                    name_to_assign_to_channel='chan_PD{}'.format(PDchans[n]))

        if rate !=0 and samps_per_chan != 0:
            self.PDtask.timing.cfg_samp_clk_timing(
                    rate=rate,
                    sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                    samps_per_chan=samps_per_chan)
            if not triggerchannelname == 0:
            #  el chanel name correcto PFI9 es la USER1 A (out1)
                self.PDtask.triggers.start_trigger.cfg_dig_edge_start_trig(
                                trigger_source=triggerchannelname,
                                trigger_edge = nidaqmx.constants.Edge.RISING)

# %%---- done
    def done(self):
        """ stop and close all the channels"""
        try:
            self.PDtask.stop()  # PDs
            self.PDtask.close()
        except:  pass

        self.channelramp = False
        self.channelsteps = False

# %%--- Step Cosas --------------
    def stepLine(self):
        """ a pesar de ser Step, hago toda una linea y despues la dibujo"""
        tic = ptime.time()

        for i in range(self.numberofPixels):

            pi_device.MOV('A', self.allstepsx[i, self.dy])
            while not all(pi_device.qONT().values()):
                time.sleep(0.01)

            PDstep = self.PDtask.read(50)  # algun numero logico
            self.PDtask.wait_until_done()

            self.PDtask.stop()

            valor = np.mean(PDstep[PD_channels[self.color_scan]])
            self.image[i, self.numberofPixels-1-self.dy] = valor
#        print( "tiempo por linea", time.time()-tic, self.linetime)

# --stepScan ---
    def stepupdate(self):
        """the step clock calls this function"""
        self.stepLine()
        tic = ptime.time()
        pi_device.MOV(['A','B'], [self.allstepsx[0,self.dy], self.allstepsy[1, self.dy]])

        self.img.setImage(self.image, autoLevels=self.autoLevels)

        while not all(pi_device.qONT().values()):
            time.sleep(0.01)

#        print(ptime.time()-tic, "tiempo fuera de la linea")
        if self.dy < self.numberofPixels-1:
            self.dy = self.dy + 1
        else:
            self.steptimer.stop()
            print(ptime.time()-self.tic, "Tiempo imagen completa.")
            if self.VideoCheck.isChecked():
                self.saveFrame()  # para guardar siempre
            self.steptimer.stop()
            if self.CMcheck.isChecked():
                self.CMmeasure()
                self.goCM()
            if self.Continouscheck.isChecked():
                self.liveviewStart()
            else:
#                self.MovetoStart()
#                self.done()
                self.liveviewStop()

    def Steps(self):

#    Barrido x: Primal signal
        startX = float(self.initialPosition[0])
        sizeX = self.scanRange
        Npuntos = self.numberofPixels
        gox = (np.linspace(0, sizeX, Npuntos) + startX)
        self.allstepsx = np.transpose(np.tile(gox, (self.numberofPixels, 1)))
    # a matrix [i,j] where i go for the complete ramp and j evolves in y lines
#        self.gox = gox

#    Barrido y: secondary signal
        startY = float(self.initialPosition[1])
        goy = np.ones(Npuntos) * startY
        self.allstepsy = np.zeros((self.numberofPixels, self.numberofPixels))
        stepy = self.scanRange / self.numberofPixels
        for j in range(len(self.allstepsy)):
            self.allstepsy[:, j] = goy + (j) * stepy

    # para el XZ, YZ
#        if self.PSFMode.currentText() == 'XY normal psf':
#            print("escaneo x y normal S")
#
#        elif self.PSFMode.currentText() == 'XZ':
#            # print("intercambio y por z S")
#            goy = np.ones(len(self.allstepsx)) * startY
#            self.allstepsy = np.tile(goy, (self.numberofPixels, 1))
#
#        elif self.PSFMode.currentText() == 'YZ':
#            # print("intercambio x por y S")
#            self.allstepsy = self.allstepsx - startX + startY
#            gox = np.ones(len(self.allstepsy)) * startX
#            self.allstepsx = np.tile(gox, (self.numberofPixels, 1))

# %% ---Move----------------------------------------
    def move(self, axis, dist):
        """moves the position along the axis specified a distance dist."""
        pos = pi_device.qPOS()
        inicial = 0
#        print(pos)
        if axis == 'x':
            axes = 'A'
            inicial = pos[axes]
        elif axis == 'y':
            axes = 'B'
            inicial = pos[axes]
        elif axis == 'z':
            axes = 'C'
            inicial = pos[axes]
        else:
            print("Pone un eje conocido! (x,y,z)")

        target = dist + inicial
        pi_device.MOV(axes, target)
        while not all(pi_device.qONT(axes).values()):
            time.sleep(0.01)
        pos = pi_device.qPOS()
        self.xLabel.setText(str(pos['A']))
        self.yLabel.setText(str(pos['B']))
        self.zLabel.setText(str(pos['C']))
    # TODO: quizas promediar

    def zMoveUp(self, algo=1):
        self.move('z', algo*float(getattr(self, 'z' + "StepEdit").text()))
        self.zDownButton.setEnabled(True)
        self.zDownButton.setStyleSheet(
            "QPushButton { background-color: }")
        self.zStepEdit.setStyleSheet(" background-color: ")

    def zMoveDown(self, algo=1):
        PosZ = self.initialPosition[2]
        if PosZ < algo*float(getattr(self, 'z' + "StepEdit").text()):
            print("OJO!, te vas a Z's negativos")
            self.zStepEdit.setStyleSheet(" background-color: red; ")
#            setStyleSheet("color: rgb(255, 0, 255);")
        else:
            self.move('z', -algo*float(getattr(self, 'z' + "StepEdit").text()))
            self.zStepEdit.setStyleSheet(" background-color: ")
            if self.initialPosition[2] == 0:  # para no ir a z negativo
                self.zDownButton.setStyleSheet(
                    "QPushButton { background-color: orange; }")
        if PosZ == 0:  # para no ira z negativo
            self.zDownButton.setStyleSheet(
                "QPushButton { background-color: red; }"
                "QPushButton:pressed { background-color: blue; }")
            self.zDownButton.setEnabled(False)

# %% Go Cm, go Gauss y go to
    def goCM(self):
        rango2 = self.scanRange/2
        self.zgotoLabel.setStyleSheet(" background-color: ")
        print("arranco en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

        startX = float(self.xLabel.text())
        startY = float(self.yLabel.text())
        self.moveto((float(self.CMxValue.text()) + startX) - rango2,
                    (float(self.CMyValue.text()) + startY) - rango2,
                    float(self.zLabel.text()))

        print("termino en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

    def goGauss(self):
        rango2 = self.scanRange/2
        self.zgotoLabel.setStyleSheet(" background-color: ")
        print("arranco en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

        startX = float(self.xLabel.text())
        startY = float(self.yLabel.text())
        self.moveto((float(self.GaussxValue.text()) + startX) - rango2,
                    (float(self.GaussyValue.text()) + startY) - rango2,
                    float(self.zLabel.text()))

        print("termino en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

# ---goto. Boton para ir a una posicion especifica

    def goto(self):

        if float(self.zgotoLabel.text()) < 0:
            QtGui.QMessageBox.question(self, '¿¡ Como pusiste z negativo !?',
                                       'Algo salio mal. :(  Avisar!!)')
            print("Z no puede ser negativo!!!")
            self.zgotoLabel.setStyleSheet(" background-color: red")
            time.sleep(1)

        else:
            self.zgotoLabel.setStyleSheet(" background-color: ")
            print("arranco en", float(self.xLabel.text()),
                  float(self.yLabel.text()), float(self.zLabel.text()))

            self.moveto(float(self.xgotoLabel.text()),
                        float(self.ygotoLabel.text()),
                        float(self.zgotoLabel.text()))

            print("termino en", float(self.xLabel.text()),
                  float(self.yLabel.text()), float(self.zLabel.text()))

            if float(self.zLabel.text()) == 0:  # para no ir a z negativo
                self.zDownButton.setStyleSheet(
                    "QPushButton { background-color: red; }"
                    "QPushButton:pressed { background-color: blue; }")
                self.zDownButton.setEnabled(False)
            else:
                self.zDownButton.setStyleSheet(
                    "QPushButton { background-color: }")
                self.zDownButton.setEnabled(True)

            self.paramChanged()

# # ---moveto ---
    def moveto(self, x, y, z):
        """moves the position along the axis to a specified point.
        Cambie todo paraque ande con la PI"""
        axis = ['A', 'B', 'C']
        targets = [x, y, z]
        pi_device.MOV(axis, targets)
        while not all(pi_device.qONT(axis).values()):
            time.sleep(0.01)
        pos = pi_device.qPOS()
        self.xLabel.setText(str(pos['A']))
        self.yLabel.setText(str(pos['B']))
        self.zLabel.setText(str(pos['C']))
    # TODO: quizas promediar

# %% ---  Shutters zone ---------------------------------
    """esto seguro se puede hacer mejor. No tiene sentido tener 4 cosas copiadas
    Con algo tipo self.shutter3button.clicked.connect(lambda: self.openShutter(shutter[3]))"""
    def shutter0(self):  # 532
        if self.shutter0button.isChecked():
            self.openShutter(shutters[0])
        else:
            self.closeShutter(shutters[0])

    def shutter1(self):  # 640
        if self.shutter1button.isChecked():
            self.openShutter(shutters[1])
        else:
            self.closeShutter(shutters[1])

    def shutter2(self):  # 405
        if self.shutter2button.isChecked():
            self.openShutter(shutters[2])
        else:
            self.closeShutter(shutters[2])

    def shutter3(self):
        if self.shutter3button.isChecked():
            self.openShutter(shutters[3])
        else:
            self.closeShutter(shutters[3])

    def openShutter(self, p):
        for i in range(len(shutters)):
            if p == shutters[i]:
                self.shuttersignal[i] = False
        self.shuttertask.write(self.shuttersignal, auto_start=True)
#        print(self.shuttersignal)
        self.checkShutters()
        print("open", p)

    def closeShutter(self, p):
        for i in range(len(shutters)):
            if p == shutters[i]:
                self.shuttersignal[i] = True
        self.shuttertask.write(self.shuttersignal, auto_start=True)
#        print(self.shuttersignal)
        self.checkShutters()
        print("close", p)

    def checkShutters(self):
        if not self.shuttersignal[0]:
            self.shutter0button.setChecked(True)
        else:
            self.shutter0button.setChecked(False)
        if not self.shuttersignal[1]:
            self.shutter1button.setChecked(True)
        else:
            self.shutter1button.setChecked(False)
        if not  self.shuttersignal[2]:
            self.shutter2button.setChecked(True)
        else:
            self.shutter2button.setChecked(False)
        if not  self.shuttersignal[3]:
            self.shutter3button.setChecked(True)
        else:
            self.shutter3button.setChecked(False)

    def shuttersChannelsNidaq(self):
        try:
            self.shuttertask = nidaqmx.Task("shutter")
            for n in range(len(shutters)):
                self.shuttertask.do_channels.add_do_chan(
                    lines="Dev1/port0/line{}".format(shutterschan[n]),
                    line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE)
            self.shuttering = True
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))

    def closeAllShutters(self):
        for i in range(len(shutters)):
            self.shuttersignal[i] = True
        self.shuttertask.write(self.shuttersignal, auto_start=True)
        self.checkShutters()
        print("cierra shutters")  # , self.shuttersignal)

# %%--- MovetoStart ---
    def MovetoStart(self):
        """ When called, it gets to the start point"""
        tic = ptime.time()
        startX = float(self.initialPosition[0])
        startY = float(self.initialPosition[1])
        startZ = float(self.initialPosition[2])
        self.moveto(startX, startY, startZ)

#        self.dy = 0  # no va mas!
        toc = ptime.time()
#        print("\n tiempo movetoStart (ms)", (toc-tic)*10**3, "\n")

# %%--- ploting in live
    def plotLive(self):
        tic = ptime.time()
        rango = self.scanRange
        texts = [getattr(self, ax + "Label").text() for ax in ["x", "y", "z"]]
        initPos = [re.findall(r"[-+]?\d*\.\d+|[-+]?\d+", t)[0] for t in texts]

        x = np.linspace(0, rango, self.numberofPixels) + float(initPos[0])
        y = np.linspace(0, rango, self.numberofPixels) + float(initPos[1])
        X, Y = np.meshgrid(x, y)
        fig, ax = plt.subplots()
        p = ax.pcolor(X, Y, np.transpose(self.image), cmap=plt.cm.jet)
        fig.colorbar(p)
        ax.set_xlabel('x [um]')
        ax.set_ylabel('y [um]')
        if self.CMplot:
            xc = int(np.floor(self.xcm))
            yc = int(np.floor(self.ycm))
            X2 = np.transpose(X)
            Y2 = np.transpose(Y)
            resol = 2
            for i in range(resol):
                for j in range(resol):
                    ax.text(X2[xc+i, yc+j], Y2[xc+i, yc+j], "CM", color='m')
            Normal = self.scanRange / self.numberofPixels  # Normalizo
            ax.set_title((self.xcm*Normal+float(initPos[0]),
                          self.ycm * Normal + float(initPos[1])))
        if self.GaussPlot:
            (height, x, y, width_x, width_y) = self.params
            xg = int(np.floor(x))  # self.GaussxValue
            yg = int(np.floor(y))  # self.GaussyValue
#            X2 = np.transpose(X)
#            Y2 = np.transpose(Y)
            resol = 2
            xsum, ysum = 0, 0
            for i in range(resol):
                for j in range(resol):
                    ax.text(X[xg+i, yg+j], Y[xg+i, yg+j], "Ga", color='m')
#                    ax.text(X2[xc+i, yc+j], Y2[xc+i, yc+j], "Ga", color='m')
                    xsum = X[xg+i, yg+j] + xsum
                    ysum = Y[xg+i, yg+j] + ysum
            xmean = xsum / (resol**2)
            ymean = ysum / (resol**2)
            ax.text(xmean, ymean, "✔", color='r')
            ax.set_title("Centro en x={:.3f}, y={:.3f}".format(xmean, ymean))
            plt.text(0.95, 0.05, """
                    x : %.1f
                    y : %.1f """ % (X[xg, yg], Y[xg, yg]),
                     fontsize=16, horizontalalignment='right',
                     verticalalignment='bottom', transform=ax.transAxes)
        plt.show()
        toc = ptime.time()
#        print("\n tiempo Plotlive", toc-tic, "\n")

# %%--- SaveFrame ---
    def save_name_update(self):
        self.edit_Name = str(self.edit_save.text())
        self.NameNumber = 0

    def saveFrame(self):
        """ Config the path and name of the file to save, and save it"""
        try:
            filepath = self.main.file_path
            # nombre con la fecha -hora
            name = str(filepath + "/" + str(self.edit_save.text()) + ".tiff")
            if self.imagecheck.isChecked():
                guardado = Image.fromarray(
                                         np.transpose(np.flip(self.image2, 1)))
            else:
                guardado = Image.fromarray(
                                         np.transpose(np.flip(self.image, 1)))

            guardado.save(name)
            self.NameNumber = self.NameNumber + 1
            self.edit_save.setText(self.edit_Name + str(self.NameNumber))
            print("\n Image saved\n")
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))


# %% GaussFit
    def GaussFit(self):
        tic = ptime.time()
        self.data = np.transpose(self.image)  # np.flip(np.flip(self.image,0),1
        params = fitgaussian(self.data)
        self.fit = gaussian(*params)
        self.params = params

        new_params = fitgaussian(self.image)
        (height, x, y, width_x, width_y) = new_params

        Normal = self.scanRange / self.numberofPixels  # Normalizo
        xx = x*Normal
        yy = y*Normal

        if 0 < xx < self.scanRange and 0 < yy < self.scanRange:
            self.GaussxValue.setText("{:.2}".format(xx))
            self.GaussyValue.setText("{:.2}".format(yy))
            self.point_graph_Gauss.setData([x], [y])
            self.vb.addItem(self.point_graph_Gauss)
            self.GaussPlot = True
        else:
            self.GaussxValue.setText("{:.2}".format(np.nan))
            self.GaussyValue.setText("{:.2}".format(np.nan))
            print("OJO, el ajuste gaussiano no dio bien")
            try:
                self.vb.removeItem(self.point_graph_Gauss)
            except:
                pass

        tac = ptime.time()
        print(np.round((tac-tic)*10**3, 3), "(ms)Gauss fit\n")

# %% CMmeasure
    def CMmeasure(self):

        tic = ptime.time()
        Z = self.image
        
        #Zn = stats.norm.pdf(Z)
        #hist, bins = np.histogram(Zn.ravel(), normed=True, bins=100)
        #threshold = bins[np.cumsum(hist)*(bins[1] - bins[0]) > 0.7][0]
        #Zmask = np.ma.masked_less(Zn,threshold)
        #xcm, ycm = ndimage.measurements.center_of_mass(Zmask)

        xcm, ycm = ndimage.measurements.center_of_mass(Z)
        
        self.xcm = xcm
        self.ycm = ycm
        Normal = self.scanRange / self.numberofPixels
        self.CMxValue.setText("{:.2}".format(xcm*Normal))
        self.CMyValue.setText("{:.2}".format(ycm*Normal))

        self.point_graph_CM.setData([xcm], [ycm])
        self.vb.addItem(self.point_graph_CM)

        self.CMplot = True
        tac = ptime.time()
        print(np.round((tac-tic)*10**3, 3), "(ms) CM\n")


# %% FUNCIONES RUTINAS PRINTING

    def grid_read(self):
        """ select the file where the grid comes from"""
        root = tk.Tk()
        root.withdraw()

        name = filedialog.askopenfilename()  # name = "C://.../sarasa/10x15"
        f = open(name, "r")
        datos = np.loadtxt(name, unpack=True)
        f.close()
        self.grid_name = name
        self.grid_x = datos[0, :]
        self.grid_y = datos[1, :]
        print(len(self.grid_x), len(self.grid_y))
        self.particulasEdit.setText(str(len(self.grid_x)))
#        z = datos[2, :]  # siempre cero en general.
        if self.grid_plot_check.isChecked:  # si esta picado, grafica
            self.grid_plot()

    def grid_plot(self):
        """hace un plot de la grilla cargada para estar seguro que es lo que
        se quiere imprimir (nunca esta de mas)"""
        try:
            fig, ax = plt.subplots()
            plt.plot(self.grid_x, self.grid_y, 'o')
            ax.set_xlabel('x (µm)')
            ax.set_ylabel('y (µm)')
            ax.grid(True)
            plt.show()
        except IOError as e:
#            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            print("^ No hay nada cargado ^")

    def grid_create_folder(self):
        """ Crea una carpeta para este archivo particular.
        Si es una grilla, puede tener esa data en el nombre (ej: 10x15)"""
        base = os.path.basename(self.grid_name)
#        grid_name = filedialog.askopenfilename()  # para preguntar el nombre

        q = base
        w = [""]*len(q)
        j = 0
        for i in range(len(q)):
            try:
                float(q[i]) == float
                print(q[i])
                w[j] = w[j] + str(q[i])
            except:
                print("separador", q[i])
                j = j+1
        print(w)
        numeros = [int(s) for s in w if s.isdigit()]

        timestr = time.strftime("%H-%M-%S")  # %Y%m%d-
        self.old_folder = self.main.file_path  # no quiero perder el nombre anterior
        try:
            print("la grilla es de {}x{}".format(numeros[0], numeros[1]))
            new_folder = self.main.file_path + "/" + timestr +\
                "_Grilla {}x{}".format(numeros[0], numeros[1])

        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
#            print("No lo tomo como grilla, AVISAR!")
            QtGui.QMessageBox.question(self,
                                       'Algo raro paso',
                                       'No lo tomo como grilla, AVISAR!\
                                       \n Pero igual creó una carpeta',
                                       QtGui.QMessageBox.Ok)

            new_folder = self.main.file_path + "/" + timestr + "_algo"

        os.makedirs(new_folder)
        self.NameDirValue.setText(new_folder)
        self.NameDirValue.setStyleSheet(" background-color: green ; ")
        self.main.file_path = new_folder
        self.i_global = 1
        self.indice_impresionEdit.setText(str(self.i_global))


#SECUENCIA DE IMPRIMIR (LPM)

    def grid_start(self):
        """funcion que empieza el programa de imprimir una grilla"""
        self.grid_timer_traza = QtCore.QTimer()
        self.grid_timer_traza.timeout.connect(self.grid_detect_traza)

        self.grid_timer_scan = QtCore.QTimer()
        self.grid_timer_scan.timeout.connect(self.grid_detect_scan)

        self.grid_continue()

    def grid_continue(self):
        self.grid_move()
        self.grid_autofoco()
        self.grid_openshutter()
        self.grid_traza()

    def grid_move(self):
        """ se mueve siguiendo las coordenadas que lee del archivo"""

        startX = float(self.xLabel.text())
        startY = float(self.yLabel.text())

        axes=['A', 'B']
        targets = [self.grid_x[self.i_global] + startX,
                   self.grid_y[self.i_global] + startY]
        pi_device.MOV(axes, targets)
        tic=ptime.time()
        while not all(pi_device.qONT(axes).values()):
            time.sleep(0.01)

        print("se movio a", pi_device.qPOS())
        print("en un tiempo",ptime.time()-tic)

    def grid_autofoco(self):
        print("autofoco")
        multifoco = np.arange(0,
                              int(self.particulasEdit.text())-1,
                              int(self.autofocEdit.text()))

        if self.i_global in multifoco:
            print("Estoy haciendo foco en la particula =", self.i_global)
            self.focus_autocorr_rampas()

    def grid_openshutter(self):
        """ abre el shutter que se va a utilizar para imprimir"""
        for i in range(len(shutters)):
            if self.grid_laser.currentText() == shutters[i]:
                self.openShutter(shutters[i])
                self.grid_shutterabierto = shutters[i]

    def grid_traza(self):
        """ Abre la ventana nueva y mide la traza,
        preparado para detectar eventos de impresion"""
        self.main.grid_traza_control = False
        self.grid_timer_traza.start(10)  # un tiempo rapido
        self.doit()

    def grid_detect_traza(self):
        """ Espera hasta detectar el evento de impresion.
        grid_timer_traza connect here"""
        if self.main.grid_traza_control:
            self.grid_timer_traza.stop()
            if self.scan_check.isChecked():
                self.grid_scan_signal()
            else:
                self.grid_detect()

    def grid_scan_signal(self):
        self.grid_scan_control = False
        self.grid_timer_scan.start(10)  # un tiempo rapido
        self.grid_scan()

    def grid_detect_scan(self):
        """ Espera hasta detectar el scan completo.
        grid_timer_scan connect here"""
        if self.grid_scan_control:
            self.grid_timer_scan.stop()
            self.grid_detect()

    def grid_detect(self):
        """ Cuando detecta un evento de impresion y la escanea (o no), entra aca.
        Esta funcion define el paso siguiente."""

        Nmax = int(self.particulasEdit.text())-1  # self.Nmax  cantidad total de particulas

        print(" i global ", self.i_global, "?")

        if self.i_global >= Nmax:
            self.main.file_path = self.old_folder
            self.NameDirValue.setText(self.old_folder)
            self.NameDirValue.setStyleSheet(" background-color: ; ")
            self.go_reference()
            self.indice_impresionEdit.setText(str(self.i_global+1))
            QtGui.QMessageBox.question(self,
                                       'Fin',
                                       'FIN!\
                                       \n fin',
                                       QtGui.QMessageBox.Ok)
        else:
            self.i_global += 1
            self.grid_continue()

    def grid_scan(self):
        """ Hace un confocal de la particula"""
        print("grid scan")
        self.liveviewButton.setChecked(True)
        self.liveview()

    def move_z(self, dist):
        """moves the position along the Z axis a distance dist."""

        print("me muevo a z", dist)

        pi_device.MOV('C', dist)
        while not all(pi_device.qONT('C').values()):
            time.sleep(0.01)

        # update position text
        self.zLabel.setText("{}".format(np.around(float(dist), 2)))

    def focus_go_to_maximun(self):

        """ barre en z mientras mira el PD, y va al maximo de intensidad"""
        z_vector = self.z_vector_create()

        z_profile_ida, z_profile_vuelta = (self.focus__rampas(z_vector))
        z_max = np.max(z_profile_vuelta)

        algomax = np.zeros(len(z_profile_vuelta))
        algomax[np.where(z_profile_vuelta == z_max)[0][0]] = z_max

        print("paso go to maximun")
        self.move_z(z_vector[np.where(z_profile_vuelta == z_max)[0][0]])
        plt.plot(z_vector, z_profile_ida, label = "ida")
        plt.plot(z_vector, z_profile_vuelta, 'r', label= "vuelta")
        plt.plot(z_vector, algomax, '.m')
 
        plt.xlabel('z position [µm]')
        plt.ylabel(' PD [V]')
        plt.title("go to maximun")
        plt.legend()
        plt.show()

    def focus_openshutter(self):
        """ abre el shutter con el que se hace foco"""
        for i in range(len(shutters)):
            if self.focus_laser.currentText() == shutters[i]:
                self.openShutter(shutters[i])
                self.focus_shutterabierto = shutters[i]

    def z_vector_create(self):
        Npasos = 128  # El mismo Npasos de gotomax # TODO: algun numero de pasos a definir (50 dice en algun lado)
        z_start = float(self.zLabel.text()) - 15  # algun rango a barrer en um
        z_end = float(self.zLabel.text()) + 15
        if z_start < 0:
            z_start = 0
        if z_end > 200:
            z_end= 200
        return np.linspace(z_start, z_end, Npasos)

    def focus_lock_focus_rampas(self):
        """ guarda el patron de intensidades, barriendo z en el foco actual"""
        tiempo_lock_focus_tic = ptime.time()
        z_antes = float(self.zLabel.text())  # guardo donde estaba
        self.z_vector = self.z_vector_create()

        self.z_profile, self.z_profilevuelta = self.focus__rampas(self.z_vector)
#        self.z_profile = z_profiles[PD_channels[color]]
        self.locked_focus = True

        self.move_z((z_antes))
        self.focus_lock_button.setStyleSheet(
                "QPushButton { background-color: ; }"
                "QPushButton:pressed { background-color: blue; }")

        print("tiempo_lock_focus", ptime.time()-tiempo_lock_focus_tic)
        print("¡Foco lockeado!. (Tengo el z_profile)")
        plt.plot(self.z_profile)
        plt.show()

    def focus__rampas(self, z_vector):
        """ guarda el patron de intensidades, barriendo z en el foco actual"""
        tiempo_lock_focus_tic = ptime.time()

        Npasos = len(z_vector)
        z_profiles = np.zeros((Npasos, len(PDchans)))  # ver si no es fila

        WTRtime = np.ceil(((self.pixelTime)) / (servo_time))#(self.pixelTime)) / (servo_time))
    # 0.00040(s)*WTRtime*Npoints = (self.pixelTime(s))*Npoints (tiempo rampa)
        print("WTRtime", WTRtime)
        sampleRate_posta = 1/(WTRtime*servo_time)
        print("samplesrate",self.sampleRate, sampleRate_posta)

        pi_device.WTR(3, WTRtime, 0)
        nciclos=1
        pi_device.WGC(3, nciclos)

        pi_device.WOS(3,z_vector[0])  # aditional offset needed

        Nspeed = np.ceil(int(Npasos / 10))
        Npoints = int((Npasos + (Nspeed*2))*2)
        center = int(Npoints/2)
        amplitudz = z_vector[-1]

#       tabla, init, Nrampa, appen, center speed, amplit, offset, lenght
        pi_device.WAV_RAMP(3, 1, Npoints, "X", center,
                           Nspeed, amplitudz, 0, Npoints)

        pi_device.TWC()  # Clear all triggers options

        pi_device.TWS([1,2,3],[1,1,1],[1,1,1])  # config a "High" signal (1) in /
        #                         points 1 from out 1,2 & 3 
        pi_device.CTO(3,1,0.005)  # config param 1 (dist for trigger) in 0.005 µm from out 1

        triggername = "PFI7"  # out 3. cable hasta la bornera A

        self.move_z((z_vector[0]))
        while not all(pi_device.qONT().values()):
            # es solo por si el MOV tarda 
            time.sleep(0.01)

        focus_laser = (self.focus_laser.currentText())

        self.channel_PD_todos(self.sampleRate, Npoints, triggername)  # PDtask

        self.PDtask.start()
        self.focus_openshutter()
        pi_device.WGO(3, True)
        z_profiles = self.PDtask.read(Npoints)  # get all points. Need to erase the acelerated zones
        while any(pi_device.IsGeneratorRunning().values()):
            time.sleep(0.01)  # espera a que termine
        pi_device.WGO(3, False)
        self.closeShutter(self.focus_shutterabierto)

        self.PDtask.stop()
        self.PDtask.close()

        print("tiempo_rampas", ptime.time()-tiempo_lock_focus_tic)
        print("rampas pasando")
        imzida = z_profiles[PD_channels[focus_laser]][int(Nspeed):int(center-Nspeed)]
        imzvuelta = z_profiles[PD_channels[focus_laser]][int(center+Nspeed):-int(Nspeed)]
        return imzida, np.flip(imzvuelta)


    def focus_autocorr_rampas(self):
        """ correlaciona la medicion de intensidad moviendo z,
        respecto del que se lockeo con loc focus RAMPAS"""
        if self.locked_focus:
            tiempo_autocorr_tic = ptime.time()

            z_profile_lock = self.z_profile

            new_profileida, new_profilevuelta = self.focus__rampas(self.z_vector)
            correlation = np.correlate(new_profileida, z_profile_lock, "same")
            indicemax = np.argmax(correlation)

            self.move_z(self.z_vector[indicemax])

            tiempo_autocorr_toc = ptime.time()
            print("tiempo_autocorr_toc", tiempo_autocorr_toc-tiempo_autocorr_tic)

        else:
            QtGui.QMessageBox.question(self,
                                       'Autocorrelacion',
                                       'No esta lockeado el foco!',
                                       QtGui.QMessageBox.Ok)
            print("¡¡No esta Lockeado el foco!!")
            self.focus_lock_button.setStyleSheet(
                    "QPushButton { background-color: red; }"
                    "QPushButton:pressed { background-color: blue; }")

    def read_pos(self):
        """lee las entradas analogicas que manda la platina y se donde estoy"""
        print("read pos")

        pos = pi_device.qPOS()
        self.xLabel.setText(str(pos['A']))
        self.yLabel.setText(str(pos['B']))
        self.zLabel.setText(str(pos['C']))
    # TODO: quizas sea util promediar en muchas medidas

    def go_reference(self):
        print("arranco go ref en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

        self.moveto(float(self.xrefLabel.text()),
                    float(self.yrefLabel.text()),
                    float(self.zrefLabel.text()))  # cambie moveto para PI

        print("termino go ref en", float(self.xLabel.text()),
              float(self.yLabel.text()), float(self.zLabel.text()))

    def set_reference(self):
        """ no lee la posicion, solo copia los numeros de uno al otro"""
        print("set ref")
        self.xrefLabel.setText(str(self.xLabel.text()))
        self.yrefLabel.setText(str(self.yLabel.text()))
        self.zrefLabel.setText(str(self.zLabel.text()))

# para saber si esta en potencia alta o baja
    def power_change(self):
        if self.power_check.isChecked():
            self.power_check.setText('Potencia \n BAJA')
            self.power_check.setStyleSheet("color: rgb(12, 183, 242); ")
        else:
            self.power_check.setText('Potencia \n ALTA')
            self.power_check.setStyleSheet("color: rgb(155, 064, 032); ")

    def scan_change(self):
        if self.scan_check.isChecked():
            self.scan_check.setText('scan? = SI')
            self.scan_check.setStyleSheet("color: orange; ")
        else:
            self.scan_check.setText('scan? = NO')
            self.scan_check.setStyleSheet("color: blue; ")

# Con esta funcion me encargo de que los menus tengan colores
    def color_menu(self, QComboBox):
        """ le pongo color a los menus"""
        if QComboBox.currentText() == shutters[0]:  # verde
            QComboBox.setStyleSheet("QComboBox{color: rgb(0,128,0);}\n")
        elif QComboBox .currentText() == shutters[1]:  # rojo
            QComboBox.setStyleSheet("QComboBox{color: rgb(255,0,0);}\n")
        elif QComboBox .currentText() == shutters[2]: # azul
            QComboBox.setStyleSheet("QComboBox{color: rgb(0,0,255);}\n")
        elif QComboBox .currentText() == shutters[2]: # azul
            QComboBox.setStyleSheet("QComboBox{color: rgb(100,0,0);}\n")
            
# %% Point scan , que ahora es traza
            
    def doit(self):
        print("Opening a new popup window...")
        self.w = Trace.MyPopup_traza(self.main, self)
        #self.w = MyPopup_traza(self.main, self)
        self.w.setGeometry(QtCore.QRect(750, 50, 450, 600))
        self.w.show()

    def traza_start(self):
        self.done()
        self.doit()
        print("Trazando...")

    def PointScanStop(self):
        self.w.pointtimer.stop()
        print("fin traza")

