# %% Library

import os
import tkinter as tk
from tkinter import filedialog

import numpy as np
import time

import matplotlib.pyplot as plt

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.ptime as ptime
from pyqtgraph.dockarea import Dock, DockArea

from PIL import Image

from scipy import ndimage
from scipy import optimize

import re

import nidaqmx
from pipython import GCSDevice

# %% Connection

#import Placa
from Placa import *


print(device)

# %% Main Interface

import MainWindow

# %% Interface Buttons
import setUpGUIarchivo
import scanner

#problema: como separar la clase ScanWidget

# %% Measurement

import Trace
import otrasfunciones

# %% End
app = QtGui.QApplication([])
#win = ScanWidget(device)
win = MainWindow.MainWindow()
win.show()

app.exec_()
