# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Toolbar
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

from PyQt4.QtGui import (QHBoxLayout, QHBoxLayout, QToolBar, QAction,
                         QIcon, QPixmap)
from PyQt4.QtCore import QSize, pyqtSignal, pyqtSlot, SIGNAL, SLOT

from qgis.core import *


class Toolbar(QToolBar):
    """A widget which contains tools."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dW = dockWidgetName
        self.iface = iface
        
        super(QToolBar, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'toolBar')
        self.setIconSize(self.iface.mainWindow().iconSize())
        
        self.toolBarHBoxLayout = QHBoxLayout(self)
        self.toolBarHBoxLayout.setObjectName(u'toolBarHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.selectRectangleAction = self.iface.actionSelectRectangle()
        self.selectRectangleAction.setObjectName(u'selectRectangleAction')
        self.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = self.iface.actionSelectPolygon()
        self.selectPolygonAction.setObjectName(u'selectPolygonAction')
        self.addAction(self.selectPolygonAction)

