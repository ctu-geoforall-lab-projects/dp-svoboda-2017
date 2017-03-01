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

from qgis.core import *

from pustack import loadvfk_puwidget, edit_puwidget, checkanalysis_puwidget


class StackedWidget(QStackedWidget):
    """A stacked widget."""
    
    def __init__(self, parentWidget, dockWidgetName, iface, pluginDir):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
            pluginDir (str): A plugin directory.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        self.pluginDir = pluginDir
        
        super(StackedWidget, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'stackedWidget')
        
        self.openTabSignalMapper = QSignalMapper(self)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.loadVfkPuWidget = loadvfk_puwidget.LoadVfkPuWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir)
        self.dW.toolBar.loadVfkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolBar.loadVfkAction, 0)
        self.addWidget(self.loadVfkPuWidget)
        
        self.editPuWidget = edit_puwidget.EditPuWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir)
        self.dW.toolBar.editAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolBar.editAction, 1)
        self.addWidget(self.editPuWidget)
        
        self.checkAnalysisPuWidget = \
            checkanalysis_puwidget.CheckAnalysisPuWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir)
        self.dW.toolBar.checkAnalysisAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(
            self.dW.toolBar.checkAnalysisAction, 2)
        self.addWidget(self.checkAnalysisPuWidget)
        
        self.openTabSignalMapper.mapped.connect(self.setCurrentIndex)
        
        self.currentChanged.connect(
            self.dW.statusBar.change_text)

