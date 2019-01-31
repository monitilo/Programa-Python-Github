# %% Main Window

import os
import tkinter as tk
from tkinter import filedialog
from pyqtgraph.Qt import QtGui
import time
#import Placa
from Placa import *
print("aa")
from setUpGUIarchivo import setUpGUI

import scanner

class MainWindow(QtGui.QMainWindow):
#TOsDO: Cartel para preguntar si estas seguro que queres salir
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
                                           QtGui.QMessageBox.No |
                                           QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes:
            print("YES")
            event.accept()
            self.close()
            self.form_widget.liveviewStop()
            pi_device.CloseConnection()

        else:
            event.ignore()
            print("NO")

    def newCall(self):
        print('New')

    def openCall(self):
        namebien = (self.form_widget.NameDirValue.text()).replace("/", "\\")
        os.startfile(namebien)
#        os.startfile(self.file_path)
        print('Open: ', self.file_path)

    def exitCall(self):
        self.closeEvent()  # ver si anda así.

    def localDir(self):
        print('poner la carpeta donde trabajar')
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        if not file_path:
            print("No elegiste nada")
        else:
            self.file_path = file_path
            print("direccion elegida: \n", self.file_path, "\n")
            self.form_widget.NameDirValue.setText(self.file_path)
            self.form_widget.NameDirValue.setStyleSheet(" background-color: ")
    #        self.form_widget.paramChanged()

# TODO: para que sea mas parecido al labview le puedo poner toda la direccion \
# donde guardar; asi no lo pregunta

    def create_daily_directory(self):
        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askdirectory()
        if not file_path:
            print("No elegiste ==> No crea la carpeta")
        else:
            timestr = time.strftime("%Y-%m-%d")  # -%H%M%S")

            newpath = file_path + "/" + timestr
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                print("Carpeta creada!")
            else:
                print("Ya existe esa carpeta")
            self.file_path = newpath
            self.form_widget.NameDirValue.setText(self.file_path)
            self.form_widget.NameDirValue.setStyleSheet(" background-color: ;")

    def save_docks(self):  # Funciones para acomodar los Docks
        self.form_widget.state = self.form_widget.dockArea.saveState()

    def load_docks(self):
        self.form_widget.dockArea.restoreState(self.form_widget.state)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        # TODO: Poner toda la ruta hasta la carpeta donde guarda: os.makedirs(newpath)
        self.file_path = os.path.abspath("")  # direccion actual. Se puede poner C://Julian etc...
        self.setWindowTitle("PIPrintingPy")  # Nombre de la ventana

    # Create new action
        openAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Open Dir', self)
        openAction.setShortcut('Ctrl+O')  # que sea .png no que que logra...
        openAction.setStatusTip('Open document')
        openAction.triggered.connect(self.openCall)

    # Create exit action
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

    # Create de file location action
        localDirAction = QtGui.QAction(QtGui.QIcon('Dir.png'), '&Select Dir', self)
        localDirAction.setStatusTip('Select the work folder')
        localDirAction.setShortcut('Ctrl+S')
        localDirAction.triggered.connect(self.localDir)

    # Create de create daily directory action
        dailyAction = QtGui.QAction(QtGui.QIcon('Daily_directory.png'), '&Create daily Dir', self)
        dailyAction.setStatusTip('Create the work folder')
        dailyAction.setShortcut('Ctrl+D')
        dailyAction.triggered.connect(self.create_daily_directory)

    # Create de create daily directory action
        save_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Save Docks', self)
        save_docks_Action.setStatusTip('Saves the Actual Docks configuration')
        save_docks_Action.setShortcut('Ctrl+p')
        save_docks_Action.triggered.connect(self.save_docks)

    # Create de create daily directory action
        load_docks_Action = QtGui.QAction(QtGui.QIcon('algo.png'), '&Restore Docks', self)
        load_docks_Action.setStatusTip('Load a previous Docks configuration')
        load_docks_Action.setShortcut('Ctrl+l')
        load_docks_Action.triggered.connect(self.load_docks)

    # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(localDirAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(dailyAction)
        fileMenu.addAction(exitAction)

        fileMenu2 = menuBar.addMenu('&Docks config')
        fileMenu2.addAction(save_docks_Action)
        fileMenu2.addAction(load_docks_Action)
#        fileMenu3 = menuBar.addMenu('&Local Folder')
#        fileMenu3.addAction(localDiraction)
        fileMenu4 = menuBar.addMenu('&<--Selecciono la carpeta desde aca!')
        fileMenu4.addAction(openAction)

        self.form_widget = setUpGUI(self, device)
        self.setCentralWidget(self.form_widget)
        self.setGeometry(10, 40, 600, 550)  # (PosX, PosY, SizeX, SizeY)
        self.save_docks()

#        self.umbralEdit = self.form_widget.umbralEdit
        self.grid_traza_control = True  # lo usa la traza
