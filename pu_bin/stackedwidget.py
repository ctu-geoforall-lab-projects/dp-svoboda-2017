# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StackedWidget
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

from PyQt4.QtGui import QStackedWidget
from PyQt4.QtCore import QSignalMapper

from loadvfk_frame import LoadVfkFrame
from edit_frame import EditFrame
from check_frame import CheckFrame


class StackedWidget(QStackedWidget):
    """A stacked widget that stores several other widgets."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        super(QStackedWidget, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'stackedWidget')
        
        self.openTabSignalMapper = QSignalMapper(self)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.loadVfkFrame = LoadVfkFrame(self, self.dWName, self.iface, self.dW)
        self.addWidget(self.loadVfkFrame)
        self.dW.toolbar.loadVfkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.loadVfkAction, 0)
        
        self.editFrame = EditFrame(self, self.dWName, self.iface, self.dW)
        self.addWidget(self.editFrame)
        self.dW.toolbar.editAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.editAction, 1)
        
        self.checkFrame = CheckFrame(self, self.dWName, self.iface, self.dW)
        self.addWidget(self.checkFrame)
        self.dW.toolbar.checkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.checkAction, 2)
        
        self.openTabSignalMapper.mapped.connect(self.setCurrentIndex)
        
        self.currentChanged.connect(
            self.dW.statusbar._change_text_statusbar)

