# %% ScanWidget
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
import pyqtgraph.ptime as ptime
import numpy as np
from Placa import *
#from setUpGUI import *
class scannerWidget(QtGui.QFrame):

    def __init__(self, main, device=device, *args, **kwargs):  # agregue device

        print('SCANNER INSTANCIADO')
        super().__init__(*args, **kwargs)

        self.main = main
        self.nidaq = device
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

# %%--- SaveFrame --

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
        plt.plot(z_vector, z_profile_ida)
        plt.plot(z_vector, z_profile_vuelta, 'r')
        plt.plot(z_vector, algomax, '.m')
        plt.show()

    def focus_openshutter(self):
        """ abre el shutter con el que se hace foco"""
        for i in range(len(shutters)):
            if self.focus_laser.currentText() == shutters[i]:
                self.openShutter(shutters[i])
                self.focus_shutterabierto = shutters[i]

    def z_vector_create(self):
        Npasos = self.numberofPixels  # El mismo Npasos de gotomax # TODO: algun numero de pasos a definir (50 dice en algun lado)
        z_start = float(self.zLabel.text()) - 30  # algun rango a barrer
        z_end = float(self.zLabel.text()) + 30
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

    # TODO: averiguar que hace y/o cuanto tarda labview

        self.z_profile = self.focus__rampas(self.z_vector)
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

        pi_device.WOS(3,0)  # aditional offset = 0

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

            Npasos = len(self.z_vector)
            Ncorrelations = 6  # TODO: a definir.... 50?  # quizas no
            new_profileida = np.zeros((Ncorrelations, Npasos))
            new_profilevuelta = np.zeros((Ncorrelations, Npasos))
            z_vector_corr = np.zeros((Ncorrelations, Npasos))
            correlations = np.zeros((Npasos))
            maxcorr = np.zeros(Ncorrelations)
            meancorr = np.zeros(Ncorrelations)
            z_profile_lock = self.z_profile

            for j in range(Ncorrelations):
                z_vector_corr[j, :] = self.z_vector - (Ncorrelations/2) + j
                new_profileida[j,:], new_profilevuelta[j,:] = self.focus__rampas(z_vector_corr[j,:])
                correlations[:] = np.correlate(new_profileida[j,:],
                                               z_profile_lock, "same")
                maxcorr[j] = np.max(correlations)
                meancorr[j] = np.mean(correlations)
            print(maxcorr, meancorr, "maximo y medio Corr")
            j_final = (np.where(maxcorr == np.max(maxcorr))[0][0])
            z_max = np.max(new_profileida[j_final, :])
            donde_z_max = np.where(new_profileida[j_final, :] == z_max)

            self.move_z(z_vector_corr[j_final, donde_z_max])

            tiempo_autocorr_toc = ptime.time()
            print("tiempo_autocorr_toc", tiempo_autocorr_toc-tiempo_autocorr_tic)

        else:
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
            
# %% Point scan , que ahora es traza

    def traza_start(self):
        self.done()
        self.doit()
        print("Trazando...")

    def PointScanStop(self):
        self.w.pointtimer.stop()
        print("fin traza")

    def doit(self):
        print("Opening a new popup window...")
        self.w = MyPopup_traza(self.main, self)
        self.w.setGeometry(QtCore.QRect(750, 50, 450, 600))
        self.w.show()