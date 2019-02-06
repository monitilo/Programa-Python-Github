# -*- coding: utf-8 -*-
"""
Created on Wed Feb  6 18:36:24 2019

@author: Luciana
"""
#%%
"""Secuencia de impresión de NPs"""
#%%

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.ptime as ptime

import numpy as np
import time

from Placa import *
#import Trace

#%%
"""Interface buttons"""





#%%

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