# %% Trace
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.ptime as ptime
import time
import numpy as np

from Placa import *
#shutters = Placa.shutters
from setUpGUI import setUpGUI

from scanner import scannerWidget

class MyPopup_traza(QtGui.QWidget):
    """ new class to create a new window for the trace menu"""

    def closeEvent(self, event):
        self.stop()
        print("Paró y cerró la traza")

    def __init__(self, main, buttons, scanbuttons):
        QtGui.QWidget.__init__(self)
        super().__init__()
        self.main = main
        self.setUpGUI = buttons  # call setUpGUI
        self.scannerWidget = scanbuttons
        self.traza_Widget2 = pg.GraphicsLayoutWidget()
        self.running = False
        grid = QtGui.QGridLayout()
        self.setLayout(grid)

        self.p6 = self.traza_Widget2.addPlot(row=2, col=1, title="Traza")
        self.p6.showGrid(x=True, y=True)
        self.curve = self.p6.plot(open='y')
        self.line = self.p6.plot(open='y')
        self.line1 = self.p6.plot(open='y')
        self.line2 = self.p6.plot(open='y')

    #  buttons: play button
        self.play_pause_Button = QtGui.QPushButton('► Play / Pause || (F1)')
        self.play_pause_Button.setCheckable(True)
        self.play_pause_Button.clicked.connect(self.play_pause)
        self.play_pause_Button.setToolTip('Pausa y continua la traza (F1)')

    # Stop button
        self.stop_Button = QtGui.QPushButton('◘ Stop (F2)')
        self.stop_Button.setCheckable(False)
        self.stop_Button.clicked.connect(self.stop)
        self.stop_Button.setToolTip('Para la traza (F2)')

    # save button
        self.save_Button = QtGui.QPushButton('plot and/or save')
        self.save_Button.setCheckable(False)
        self.save_Button.clicked.connect(self.save_traza)
        self.save_Button.setToolTip('Para Guardar la traza(tambien la plotea)')
        self.save_Button.setStyleSheet(
                "QPushButton { background-color: rgb(200, 200, 10); }"
                "QPushButton:pressed { background-color: blue; }")

    # umbral

        umbralEdit = self.setUpGUI.umbralEdit
        self.umbral = float(umbralEdit.text())

        self.PointLabel = QtGui.QLabel('<strong>0.00|0.00')
        grid.addWidget(self.traza_Widget2,      0, 0, 1, 7)
        grid.addWidget(self.play_pause_Button,  1, 0)
        grid.addWidget(self.stop_Button,        1, 1)
        grid.addWidget(self.PointLabel,         1, 5)
        grid.addWidget(self.save_Button,        1, 6)
        self.setWindowTitle("Traza. (ESC lo cierra bien)")
        self.play_pause_Button.setChecked(True)
        self.PointScan()

        self.play_pause_Action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F1'), self, self.play_pause_active)

        self.stop_Action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F2'), self, self.stop)

        self.close_Action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('ESC'), self, self.close_win)

    def close_win(self):
        self.stop()
        self.close()

    def play_pause_active(self):
        '''Triggered by the play_pause_Action shortcut.'''
        if self.play_pause_Button.isChecked():
            self.play_pause_Button.setChecked(False)
        else:
            self.play_pause_Button.setChecked(True)
        self.play_pause()

    def play_pause(self):
        if self.play_pause_Button.isChecked():
            print("play")
            self.traza_openshutter()
            self.timer_inicio = ptime.time()
            if self.running:
                self.pointtimer.start(self.tiempo)
            else:
                self.PointScan()
        else:
            print("pause")
            self.scannerWidget.closeShutter(self.traza_shutterabierto)
            self.pointtimer.stop()

    def stop(self):
        print("stop")
        self.scannerWidget.closeShutter(self.traza_shutterabierto)
        try:
            self.pointtimer.stop()
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        self.running = False
        self.play_pause_Button.setChecked(False)
        try:
            self.pointtask.stop()
            self.pointtask.close()
        except:  # pass
            print("pointtasktask no estaba abierto")

    def traza_openshutter(self):
        """ abre el shutter que se va a utilizar para imprimir"""
        for i in range(len(shutters)):
            if self.scannerWidget.traza_laser.currentText() == shutters[i]:
                self.scannerWidget.openShutter(shutters[i])
                self.traza_shutterabierto = shutters[i]

    def save_traza(self, imprimiendo=False):
        try:
            print("va a aguardar")
            # filepath = self.file_path
            filepath = self.main.file_path
            timestr = time.strftime("%d%m%Y-%H%M%S")
            if imprimiendo:  # si viene de la rutina, guarda automatico con el numero de particula
                timestr = str("Particula-") + str(self.scannerWidget.i_global)
                self.setUpGUI.edit_save.setText(str(timestr))
            name = str(filepath + "/" + timestr + "-Traza" + ".txt")
            print("va a abrir el name")
            f = open(name, "w")
            np.savetxt(name,
                       np.transpose([self.timeaxis[:self.ptr1],
                                     self.data1[:self.ptr1]]),
                       header="{} y umbral={:.3}".format(
                        timestr, float(self.umbral)))
            print("va a cerrarlo")
            f.close()
            print("\n Guardo la Traza")
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))

#        fig, ax = plt.subplots()
#        plt.plot(self.timeaxis[:self.ptr1], self.data1[:self.ptr1])
#        ax.set_xlabel('Tiempo (s) (puede fallar)')
#        ax.set_ylabel('Intensity (V)')
#        plt.show()

    def PointScan(self):
        self.running = True
        self.tiempo = 1  # ms  # refresca el numero cada este tiempo
        self.Napd = int(np.round(apdrate * self.tiempo/10**3))

        self.points = np.zeros(self.Napd)
        self.points2 = np.copy(self.points)
        try:
            self.pointtask.stop()
            self.pointtask.close()
        except: pass

        self.pointtask = nidaqmx.Task('pointtaskPD')
        # Configure the analog in channel to read all the PDs
        for n in range(len(PDchans)):
            self.pointtask.ai_channels.add_ai_voltage_chan(
                physical_channel='Dev1/ai{}'.format(PDchans[n]),  # igual son [0,1,2]
                name_to_assign_to_channel='chan_PD{}'.format(PDchans[n]))

            self.pointtask.timing.cfg_samp_clk_timing(
              rate=apdrate,  # TODO: ver velocidad PD...
              sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
              source=r'100kHzTimebase',  # 1000k
              samps_per_chan=len(self.points))

        self.color_traza = self.setUpGUI.traza_laser.currentText()

        self.ptr1 = 0
        self.timeaxis = np.empty(100)
        self.data1 = np.empty(100)

    # Quiero saber cuanto tarda para que coincidan los tiempos
        self.tiemporeal = self.tiempo
        tic = ptime.time()
        self.updatePoint()
        tiic = ptime.time()
        self.tiemporeal = (tiic-tic)*2
        print("tiempo propuesto=", self.tiempo*10**3, "ms")
        print("tiempo real=", self.tiemporeal*10**3, "ms")

        self.ptr1 = 0
        self.timeaxis = np.empty(100)
        self.data1 = np.empty(100)

        self.traza_openshutter()
        self.timer_inicio = ptime.time()
        self.pointtimer = QtCore.QTimer()
        self.pointtimer.timeout.connect(self.updatePoint)
        self.pointtimer.start(self.tiemporeal)

    def updatePoint(self):

        N = len(self.points)
        lectura_total = self.pointtask.read(N)
        self.points[:] = lectura_total[PD_channels[self.color_traza]][:]

        m = np.mean(self.points)

        self.timeaxis[self.ptr1] = self.ptr1 * self.tiemporeal  # *self.tiempo
        self.data1[self.ptr1] = m
        self.ptr1 += 1
        if self.ptr1 >= self.data1.shape[0]:
            tmpdata1 = self.data1
            self.data1 = np.empty(self.data1.shape[0] * 2)
            self.data1[:tmpdata1.shape[0]] = tmpdata1
            tmptime = self.timeaxis
            self.timeaxis = np.empty(self.timeaxis.shape[0] * 2)
            self.timeaxis[:tmptime.shape[0]] = tmptime

        self.curve.setData(self.timeaxis[:self.ptr1], self.data1[:self.ptr1],
                           pen=pg.mkPen('y', width=1),
                           shadowPen=pg.mkPen('w', width=3))

        M = 10
        M2 = 10
        if self.ptr1 < M:
            mediochico = np.mean(self.data1[:self.ptr1])
            self.timeaxis2 = self.timeaxis[:self.ptr1]
            if self.ptr1 < M2:
                mediochico2 = np.mean(self.data1[:self.ptr1])
            else:
                mediochico2 = np.mean(self.data1[:self.ptr1-M2])
        else:
            mediochico = np.mean(self.data1[self.ptr1-M:self.ptr1])
#            self.timeaxis2 = self.timeaxis[self.ptr1-M:self.ptr1]

            mediochico2 = np.mean(self.data1[self.ptr1-M-M2:self.ptr1-M2])

        self.PointLabel.setText("<strong>{:.3}|{:.3}".format(
                                float(mediochico), float(mediochico2)))

        if mediochico >= mediochico2*float(self.umbral):
            self.PointLabel.setStyleSheet(" background-color: orange")
        else:
            self.PointLabel.setStyleSheet(" background-color: ")

        try:  # no se bien en que caso sirve esto que puse aca
            if self.timer_inicio == 0:
                self.timer_inicio = 0
        except:
            self.timer_inicio = ptime.time()

    # Este if not es el que define si se esta corriendo una grilla
        if not self.main.grid_traza_control:
            if abs(mediochico) > abs(mediochico2)*float(self.umbral) or (ptime.time() - self.timer_inicio) > float(self.setUpGUI.tmaxEdit.text()):
                print("medio=", np.round(mediochico), np.round(mediochico2))
                self.save_traza(True)
                self.closeShutter(self.color_traza)
                self.stop()
                self.close_win()
                self.main.grid_traza_control = True