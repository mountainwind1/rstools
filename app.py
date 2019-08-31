#
#
#
import os.path as osp
import functools
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
#from . import utils
import utils
import config
from config import get_config
import widgets
#from . import widgets
from widgets import ToolBar
from widgets import LabelQListWidget
from widgets import Canvas
from widgets import ZoomWidget

class MainWindow(QtWidgets.QMainWindow):
    __appname__ = "Rs"
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = 0, 1, 2
    def __init__(self):
        #__appname__ = "Rs"
        super(MainWindow, self).__init__()
        self.setWindowTitle(self.__appname__)

        config = get_config()
        self._config = config
        self.labelList = LabelQListWidget()
        self.labelList.setParent(self)
        self.canvas = self.labelList.canvas = Canvas(
            epsilon=self._config['epsilon'],
        )
        self.canvas.zoomRequest.connect(self.zoomRequest)
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidget(self.canvas)
        scrollArea.setWidgetResizable(True)

        self.setCentralWidget(scrollArea)

        self.zoomWidget = ZoomWidget()
        # Actions
        action = functools.partial(utils.newAction, self)
        shortcuts = self._config['shortcuts']
        quit = action('&Quit', self.close, shortcuts['quit'], 'quit',
                      'Quit application')
        open_ = action('&Open', self.openFile, shortcuts['open'], 'open',
                       'Open image or label file')

        zoom = QtWidgets.QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            'Zoom in or out of the image. Also accessible with '
            '{} and {} from the canvas.'
                .format(
                utils.fmtShortcut(
                    '{},{}'.format(
                        shortcuts['zoom_in'], shortcuts['zoom_out']
                    )
                ),
                utils.fmtShortcut("Ctrl+Wheel"),
            )
        )
        self.zoomWidget.setEnabled(False)

        zoomIn = action('Zoom &In', functools.partial(self.addZoom, 1.1),
                        shortcuts['zoom_in'], 'zoom-in',
                        'Increase zoom level', enabled=False)
        zoomOut = action('&Zoom Out', functools.partial(self.addZoom, 0.9),
                         shortcuts['zoom_out'], 'zoom-out',
                         'Decrease zoom level', enabled=False)
        zoomOrg = action('&Original size',
                         functools.partial(self.setZoom, 100),
                         shortcuts['zoom_to_original'], 'zoom',
                         'Zoom to original size', enabled=False)
        fitWindow = action('&Fit Window', self.setFitWindow,
                           shortcuts['fit_window'], 'fit-window',
                           'Zoom follows window size', checkable=True,
                           enabled=False)
        fitWidth = action('Fit &Width', self.setFitWidth,
                          shortcuts['fit_width'], 'fit-width',
                          'Zoom follows window width',
                          checkable=True, enabled=False)
        # Group zoom controls into a list for easier toggling.
        zoomActions = (self.zoomWidget, zoomIn, zoomOut, zoomOrg,
                       fitWindow, fitWidth)
        self.zoomMode = self.FIT_WINDOW
        fitWindow.setChecked(Qt.Checked)
        self.scalers = {
            self.FIT_WINDOW: self.scaleFitWindow,
            self.FIT_WIDTH: self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }
        self.actions = utils.struct(
            zoom=zoom, zoomIn=zoomIn, zoomOut=zoomOut, zoomOrg=zoomOrg,
            fitWindow=fitWindow, fitWidth=fitWidth,
            zoomActions=zoomActions,

            fileMenuActions=(open_, quit),
            tool=(),
            # menu shown at right click

        )

        self.menus = utils.struct(
            file=self.menu('&File'),
            edit=self.menu('&Edit'),
            view=self.menu('&View'),
        )
        utils.addActions(
            self.menus.file,
            (
                open_,
                None,
                quit,
            ),
        )
        self.tools = self.toolbar('Tools')
        # Menu buttons on Left
        self.actions.tool = (
            open_,
        )

        self.statusBar().showMessage('%s started.' % self.__appname__)
        self.statusBar().show()

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName('%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            utils.addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


    def zoomRequest(self, delta, pos):
        canvas_width_old = self.canvas.width()
        units = 1.1
        if delta < 0:
            units = 0.9
        self.addZoom(units)

        canvas_width_new = self.canvas.width()
        if canvas_width_old != canvas_width_new:
            canvas_scale_factor = canvas_width_new / canvas_width_old

            x_shift = round(pos.x() * canvas_scale_factor) - pos.x()
            y_shift = round(pos.y() * canvas_scale_factor) - pos.y()

            self.scrollBars[Qt.Horizontal].setValue(
                self.scrollBars[Qt.Horizontal].value() + x_shift)
            self.scrollBars[Qt.Vertical].setValue(
                self.scrollBars[Qt.Vertical].value() + y_shift)

    def openFile(self, _value=False):
        if not self.mayContinue():
            return
        path = osp.dirname(str(self.filename)) if self.filename else '.'
        formats = ['*.{}'.format(fmt.data().decode())
                   for fmt in QtGui.QImageReader.supportedImageFormats()]
        # filters = "Image & Label files (%s)" % ' '.join(
        #     formats + ['*%s' % LabelFile.suffix])
        filters = "Image & Label files (%s)" % ' '.join(
            formats + ['*%s' %  '.json'])
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, '%s - Choose Image or Label file' % self.__appname__,
            path, filters)
        filename, _ = filename
        filename = str(filename)
        if filename:
            self.loadFile(filename)


    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            utils.addActions(menu, actions)
        return menu

    def addZoom(self, increment=1.1):
        self.setZoom(self.zoomWidget.value() * increment)


    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(value)

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def scaleFitWindow(self):
        """Figure out the size of the pixmap to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2
    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()