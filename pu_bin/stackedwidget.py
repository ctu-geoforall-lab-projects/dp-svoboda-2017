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

from pu_stackedwidget_frames import (loadvfk_frame, edit_frame,
                                     checkanalysis_frame)


class StackedWidget(QStackedWidget):
    """A stacked widget that stores several other widgets."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        super(StackedWidget, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'stackedWidget')
        
        self.openTabSignalMapper = QSignalMapper(self)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.loadVfkFrame = loadvfk_frame.LoadVfkFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.loadVfkFrame)
        self.dW.toolBar.loadVfkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolBar.loadVfkAction, 0)
        
        self.editFrame = edit_frame.EditFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.editFrame)
        self.dW.toolBar.editAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolBar.editAction, 1)
        
        self.checkAnalysisFrame = checkanalysis_frame.CheckAnalysisFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.checkAnalysisFrame)
        self.dW.toolBar.checkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolBar.checkAction, 2)
        
        self.openTabSignalMapper.mapped.connect(self.setCurrentIndex)
        
        self.currentChanged.connect(
            self.dW.statusBar.change_text_statusbar)

