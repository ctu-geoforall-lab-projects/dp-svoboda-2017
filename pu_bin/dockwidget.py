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

from qgis.gui import QgsMessageBar
from qgis.core import *

from status_label import StatusLabel
from toolbar import Toolbar
from stackedwidget import StackedWidget

import traceback


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
        
        self.toolbar = Toolbar(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.toolbar, 0, 0, 1, 1)
        
        self.stackedWidget = StackedWidget(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.stackedWidget, 1, 0, 1, 1)
        
        self.statusLabel = StatusLabel(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.statusLabel, 2, 0, 1, 1)
    
    def _raise_pu_error(
            self, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
        """Displays error messages.
    
        Displays error messages in the 'puPlugin' Log Messages Panel,
        statusLabel and Message Bar.
        
        For development purposes it displays traceback
        in the 'puPlugin Development' Log Messages Tab.
        
        Args:
            engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            czeLabelMsg (str): A message in the statusLabel.
            czeLabelMsg (str): A message in the Message Bar.
            duration (int): A duration of the message in the Message Bar
                             in seconds.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, statusLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        pluginName = u'PU Plugin'
        
        if czeBarMsg is None:
            czeBarMsg = czeLabelMsg
        
        QgsMessageLog.logMessage(engLogMsg, pluginName)
        self.statusLabel.text_statusLabel.emit(czeLabelMsg)
        self.iface.messageBar().pushMessage(
            pluginName, czeBarMsg , QgsMessageBar.WARNING, duration)
        
        developmentTb = u'PU Plugin Development'
        tb = traceback.format_exc()
        
        if 'None' not in tb:
            QgsMessageLog.logMessage(tb, developmentTb)
    
    class puError(Exception):
        def __init__(
                self, dW, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
            super(Exception, self).__init__(dW)
            
            self.dW = dW
            
            self.dW._raise_pu_error(
                engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7)

