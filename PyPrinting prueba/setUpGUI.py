from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea

from Placa import *
from scanner import scannerWidget

class setUpGUI(QtGui.QFrame):

    def __init__(self, main, device, *args, **kwargs):  # agregue device

        super().__init__(*args, **kwargs)

        self.main = main
        self.nidaq = device
        
        self.myscan = scannerWidget(self)
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
        self.cargar_archivo_button.clicked.connect(myscan.grid_read)
        self.cargar_archivo_button.setStyleSheet(
                "QPushButton { background-color: orange; }"
                "QPushButton:pressed { background-color: blue; }")
        self.cargar_archivo_button.setToolTip('Carga el archivo con la grilla, y lo puede plotear para ver si esta bien')

    # Print button. Que en realidad solo crea la carpeta
        self.imprimir_button = QtGui.QPushButton('IMPRIMIR (crea carpeta)')
        self.imprimir_button.setCheckable(True)
        self.imprimir_button.clicked.connect(myscan.grid_create_folder)
        self.imprimir_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.imprimir_button.setToolTip('En realidad solo crea la carpeta. El mundo es una gran mentira.')
#                "QPushButton:checked {color: white; background-color: blue;}")

    # desides if plot the positions in the grid to print. Just for  be sure
        self.grid_plot_check = QtGui.QCheckBox('plot_test?')
        self.grid_plot_check.clicked.connect(myscan.grid_plot)

    # Print button. Que en realidad solo crea la carpeta
        self.next_button = QtGui.QPushButton('Next ►')
        self.next_button.setCheckable(False)
        self.next_button.clicked.connect(myscan.grid_start)
        self.next_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.next_button.setToolTip('Empeiza o continua la grilla')

    # go ref button.
        self.go_ref_button = QtGui.QPushButton('go reference')
        self.go_ref_button.setCheckable(False)
        self.go_ref_button.clicked.connect(myscan.go_reference)
        self.go_ref_button.setStyleSheet(
                "QPushButton:pressed { background-color: blue; }")
        self.go_ref_button.setToolTip('Va a la referencia seteada')
        self.go_ref_button.setFixedWidth(80)

    # set reference button.
        self.set_ref_button = QtGui.QPushButton('set reference')
        self.set_ref_button.setCheckable(False)
        self.set_ref_button.clicked.connect(myscan.set_reference)
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
        grid_print_layout.addWidget(self.umbralLabel,             3, 3)
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
        self.focus_lock_button.clicked.connect(myscan.focus_lock_focus_rampas)
        self.focus_lock_button.setToolTip('guarda el patron en el z actual')
        self.focus_lock_button.setStyleSheet(
                "QPushButton { background-color: rgb(254,100,100) ; }"
                "QPushButton:pressed { background-color: blue; }")

    # Boton de Autocorrelacion, con el foco ya lockeado
        self.focus_autocorr_button = QtGui.QPushButton('Autocorrelacion')
        self.focus_autocorr_button.setCheckable(False)
        self.focus_autocorr_button.clicked.connect(myscan.focus_autocorr_rampas)
        self.focus_autocorr_button.setToolTip('guarda el patron nel z actual')

    # Go to maximun
        self.focus_gotomax_button = QtGui.QPushButton('go to maximun')
        self.focus_gotomax_button.setCheckable(False)
        self.focus_gotomax_button.clicked.connect(myscan.paramChangedInitialize)

        self.focus_gotomax_button.clicked.connect(myscan.focus_go_to_maximun)
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
        self.shutter0button.clicked.connect(myscan.shutter0)
        self.shutter0button.setStyleSheet("color: green; ")

        self.shutter1button = QtGui.QCheckBox('shutter Red')
        self.shutter1button.clicked.connect(myscan.shutter1)
        self.shutter1button.setStyleSheet("color: red; ")

        self.shutter2button = QtGui.QCheckBox('shutter Blue')
        self.shutter2button.clicked.connect(myscan.shutter2)
        self.shutter2button.setStyleSheet("color: blue; ")

        self.shutter3button = QtGui.QCheckBox('shutter IR (808)')
        self.shutter3button.clicked.connect(myscan.shutter3)
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
                                lambda: self.color_menu(myscan.preescan_laser))
        self.color_menu(self.preescan_laser)

    # Defino el tipo de laser que quiero para imprimir
        self.dimerscan_laser = QtGui.QComboBox()
        self.dimerscan_laser.addItems(shutters)
        self.dimerscan_laser.setCurrentIndex(2)
        self.dimerscan_laser.setToolTip('Elijo el shuter para escanear el dimero ')
        self.dimerscan_laser.setFixedWidth(80)
        self.dimerscan_laser.activated.connect(
                                lambda: self.color_menu(myscan.dimerscan_laser))
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
        self.read_pos_button.clicked.connect(myscan.read_pos)
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
        self.liveviewButton.clicked.connect(myscan.liveview)
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
        self.CMcheck.clicked.connect(myscan.CMmeasure)
        self.CMcheck.setToolTip('makes a basic measurement of\
                                the center of mass')

    # 2D Gaussian fit to estimate the center of a NP
        self.Gausscheck = QtGui.QCheckBox('Gauss fit')
        self.Gausscheck.setCheckable(False)
        self.Gausscheck.clicked.connect(myscan.GaussFit)
        self.Gausscheck.setToolTip('makes 2D Gaussian fit of the image,\
                                   and give the center')

    # save image Button
        self.saveimageButton = QtGui.QPushButton('Save Frame')
        self.saveimageButton.setCheckable(False)
        self.saveimageButton.clicked.connect(myscan.saveFrame)
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
        self.imagecheck.clicked.connect(myscan.imageplot)
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
        self.plotLivebutton.clicked.connect(myscan.plotLive)
        self.plotLivebutton.setToolTip('Plot this image with matplotlive')

    # Select the detector
        self.detectMode = QtGui.QComboBox()
        self.detectMode.addItems(detectModes)  # only PD. not ussefull anymore
        self.detectMode.setToolTip('Select the detect instrument (APD or PMT)')

    # Point scan (TRAZA)
        self.trazaButton = QtGui.QPushButton('TRAZA')
        self.trazaButton.setCheckable(False)
        self.trazaButton.clicked.connect(myscan.traza_start)
        self.trazaLabel = QtGui.QLabel('<strong>0.00|0.00')
        self.trazaButton.setToolTip('continuously measures the APDs (Ctrl+T)')

    # Scanning parameters

        self.scanRangeLabel = QtGui.QLabel('Scan range (µm)')
        self.scanRangeEdit = QtGui.QLineEdit('2')
        self.pixelTimeLabel = QtGui.QLabel('Pixel time (ms)')
        self.pixelTimeEdit = QtGui.QLineEdit('1')
        self.pixelTimeEdit.setToolTip('0.01 ms = 10 µs  :)')

        self.numberofPixelsLabel = QtGui.QLabel('Number of pixels')
        self.numberofPixelsEdit = QtGui.QLineEdit('32')
        self.pixelSizeLabel = QtGui.QLabel('Pixel size (nm)')
        self.pixelSizeValue = QtGui.QLineEdit('20')

        self.timeTotalLabel = QtGui.QLabel('total scan time (s)')
        self.timeTotalLabel.setToolTip('Is an aproximate value')

        self.onlyInt = QtGui.QIntValidator(0, 10001)
        self.numberofPixelsEdit.setValidator(self.onlyInt)
        self.onlypos = QtGui.QDoubleValidator(0, 1000, 10)
        self.pixelTimeEdit.setValidator(self.onlypos)
        self.scanRangeEdit.setValidator(self.onlypos)

        self.numberofPixelsEdit.textEdited.connect(myscan.PixelSizeChange)
        self.pixelSizeValue.textEdited.connect(myscan.NpixChange)
        self.scanRangeEdit.textEdited.connect(myscan.PixelSizeChange)

    # Defino el tipo de laser que quiero para imprimir
        self.scan_laser = QtGui.QComboBox()
        self.scan_laser.addItems(shutters)
        self.scan_laser.setCurrentIndex(2)
        self.scan_laser.setToolTip('Elijo el shuter para scanear')
        self.scan_laser.setFixedWidth(80)
        self.scan_laser.activated.connect(
                                    lambda: self.color_menu(myscan.scan_laser))
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
        subgrid.addWidget(self.scanRangeLabel,      3, 1)
        subgrid.addWidget(self.scanRangeEdit,       4, 1)
        subgrid.addWidget(self.pixelTimeLabel,      5, 1)
        subgrid.addWidget(self.pixelTimeEdit,       6, 1)
        subgrid.addWidget(self.numberofPixelsLabel, 7, 1)
        subgrid.addWidget(self.numberofPixelsEdit,  8, 1)
        subgrid.addWidget(self.pixelSizeLabel,      9, 1)
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
        self.gotoButton.pressed.connect(myscan.goto)
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
        self.CMxLabel = QtGui.QLabel('CM X')
        self.CMxValue = QtGui.QLabel('NaN')
        self.CMyLabel = QtGui.QLabel('CM Y')
        self.CMyValue = QtGui.QLabel('NaN')
        layout3.addWidget(self.CMxLabel, 3, 1)
        layout3.addWidget(self.CMxValue, 4, 1)
        layout3.addWidget(self.CMyLabel, 3, 2)
        layout3.addWidget(self.CMyValue, 4, 2)
        self.goCMButton = QtGui.QPushButton("♠ Go CM ♣")
        self.goCMButton.pressed.connect(myscan.goCM)
        layout3.addWidget(self.goCMButton, 1, 4, 1, 2)
        layout3.addWidget(self.CMcheck, 1, 1, 1, 2)

        self.GaussxLabel = QtGui.QLabel('Gauss X')
        self.GaussxValue = QtGui.QLabel('NaN')
        self.GaussyLabel = QtGui.QLabel('Gauss Y')
        self.GaussyValue = QtGui.QLabel('NaN')
        layout3.addWidget(self.GaussxLabel, 3, 4)
        layout3.addWidget(self.GaussxValue, 4, 4)
        layout3.addWidget(self.GaussyLabel, 3, 5)
        layout3.addWidget(self.GaussyValue, 4, 5)
#        layout3.addWidget(QtGui.QLabel(' '), 4, 4)
        self.goCMButton = QtGui.QPushButton("♥ Go Gauss ♦")
        self.goCMButton.pressed.connect(myscan.goGauss)
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
        
        self.dockArea = dockArea  # lo paso a self. por si lo usaba despues
# %% shortcuts todos juntos
        self.liveviewAction = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+a'), self, myscan.liveviewKey)

        self.grid_start_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F5'), self, myscan.grid_start)

        self.focus_maximun_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F8'), self, myscan.focus_go_to_maximun)

        self.grid_read_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F1'), self, myscan.grid_read)

        self.grid_autocorr_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('F9'), self, myscan.focus_autocorr_rampas)

        self.lock_focus_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('ctrl+f'), self, myscan.focus_lock_focus_rampas)

        self.lock_focus_action = QtGui.QAction(self)
        QtGui.QShortcut(
            QtGui.QKeySequence('ctrl+t'), self, myscan.traza_start)
#TODO: agregar mas Shortcuts copados (o copiar los de labview)

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
            
    def save_name_update(self):
        self.edit_Name = str(self.edit_save.text())
        self.NameNumber = 0
        
    def autoLevelset(self):
        """config the auto normalize of the scan colorbar"""
        if self.autoLevelscheck.isChecked():
            self.autoLevels = True
        else:
            self.autoLevels = False