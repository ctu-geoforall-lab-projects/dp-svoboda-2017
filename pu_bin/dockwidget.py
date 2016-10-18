# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DockWidget
                                 A QGIS plugin
 Plugin pro pozemkové úpravy
                             -------------------
        begin                : 2016-09-01
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Ondřej Svoboda
        email                : svoboond@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import QDockWidget, QWidget, QGridLayout
from PyQt4.QtCore import QMetaObject

from status_label import StatusLabel
from toolbar_widget import ToolBarWidget
from loadvfk_frame import LoadVfkFrame


class DockWidget(QDockWidget):
    """The main widget of the PU Plugin."""
    
    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.iface = iface
        
        super(DockWidget, self).__init__()
        
        dockWidgetName = u'dockWidget'
        
        self._setup_self(dockWidgetName)
        
#         self.loadVfkPushButton.clicked.connect(
#             self.loadVfkPushButton_clicked)
#         self.browseVfkLineEdit.textChanged.connect(
#             self.browseVfkLineEdit_textChanged)
    
    def _setup_self(self, dockWidgetName):
        """Sets up self.
        
        Args:
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.setObjectName(u'dockWidget')
        
        self.mainWidget = QWidget(self)
        self.mainWidget.setObjectName(u'mainWidget')
        
        self.setWidget(self.mainWidget)
        
        self.mainGridLayout = QGridLayout(self.mainWidget)
        self.mainGridLayout.setObjectName(u'mainGridLayout')
        
        self.setWindowTitle(u'PU Plugin')
        
        self._build_widgets(dockWidgetName)
    
    def _build_widgets(self, dockWidgetName):
        """Build own widgets.
        
        Args:
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.toolBarWidget = ToolBarWidget(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.toolBarWidget, 0, 0, 1, 1)
        
        self.loadVfkFrame = LoadVfkFrame(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.loadVfkFrame, 1, 0, 1, 1)
        
        self.statusLabel = StatusLabel(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.statusLabel, 2, 0, 1, 1)

