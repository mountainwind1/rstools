#
#
#
import functools
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
#from . import utils
import utils
import config
from config import get_config
import widgets
#from . import widgets
from widgets import ToolBar
from widgets import LabelQListWidget
from widgets import Canvas

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        __appname__ = "Rs"
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

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
        # Actions
        action = functools.partial(utils.newAction, self)
        shortcuts = self._config['shortcuts']
        quit = action('&Quit', self.close, shortcuts['quit'], 'quit',
                      'Quit application')
        open_ = action('&Open', self.openFile, shortcuts['open'], 'open',
                       'Open image or label file')

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

        self.statusBar().showMessage('%s started.' % __appname__)
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