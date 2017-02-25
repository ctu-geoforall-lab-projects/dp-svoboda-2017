# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToolBar
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

from PyQt4.QtGui import (QToolBar, QToolButton, QAction, QIcon, QPixmap,
                         QActionGroup)

from qgis.core import *


class ToolBar(QToolBar):
    """A widget which contains tools."""
    
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
        
        super(ToolBar, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'toolbar')
        self._set_icon_size()
        self.iface.initializationCompleted.connect(self._set_icon_size)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.openTabActionGroup = QActionGroup(self)
        
        self.loadVfkAction = QAction(self)
        self.loadVfkAction.setObjectName(u'loadVfkAction')
        self.loadVfkAction.setToolTip(u'Načtení VFK souboru')
        self.loadVfkAction.setCheckable(True)
        loadVfkIcon = QIcon()
        loadVfkIcon.addPixmap(QPixmap(':/loadvfk.png'))
        self.loadVfkAction.setIcon(loadVfkIcon)
        self.openTabActionGroup.addAction(self.loadVfkAction)
        self.addAction(self.loadVfkAction)
        self.loadVfkAction.trigger()
        
        self.editAction = QAction(self)
        self.editAction.setObjectName(u'editAction')
        self.editAction.setToolTip(u'Editace')
        self.editAction.setCheckable(True)
        editIcon = QIcon()
        editIcon.addPixmap(QPixmap(':/edit.png'))
        self.editAction.setIcon(editIcon)
        self.openTabActionGroup.addAction(self.editAction)
        self.addAction(self.editAction)
        
        self.checkAnalysisAction = QAction(self)
        self.checkAnalysisAction.setObjectName(u'checkAnalysisAction')
        self.checkAnalysisAction.setToolTip(u'Kontroly a analýzy')
        self.checkAnalysisAction.setCheckable(True)
        checkIcon = QIcon()
        checkIcon.addPixmap(QPixmap(':/checkanalysis.png'))
        self.checkAnalysisAction.setIcon(checkIcon)
        self.openTabActionGroup.addAction(self.checkAnalysisAction)
        self.addAction(self.checkAnalysisAction)
        
        self.addSeparator()
        
        self.zoomFullExtentAction = self.iface.actionZoomFullExtent()
        self.addAction(self.zoomFullExtentAction)
        
        self.zoomToSelectedAction = self.iface.actionZoomToSelected()
        self.addAction(self.zoomToSelectedAction)
        
        self.selectToolButton = QToolButton(self)
        self.selectToolButton.setObjectName(u'selectToolButton')
        self.selectToolButton.setPopupMode(1)
        
        self.selectRectangleAction = self.iface.actionSelectRectangle()
        self.selectToolButton.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = self.iface.actionSelectPolygon()
        self.selectToolButton.addAction(self.selectPolygonAction)
        
        self.selectFreehandAction = self.iface.actionSelectFreehand()
        self.selectToolButton.addAction(self.selectFreehandAction)
        
        self.selectRadiusAction = self.iface.actionSelectRadius()
        self.selectToolButton.addAction(self.selectRadiusAction)
        
        for action in self.iface.attributesToolBar().actions():
            if action.objectName() == 'ActionSelect':
                self.qgisSelectToolButton = action.defaultWidget()
                break
        
        self.qgisSelectToolButton.toggled.connect(
            self._set_default_action_selectToolButton)
        
        self._set_default_action_selectToolButton()
        
        self.addWidget(self.selectToolButton)
        
        self.selectionToolButton = QToolButton(self)
        self.selectionToolButton.setObjectName(u'selectionToolButton')
        self.selectionToolButton.setPopupMode(1)
        
        for action in self.iface.attributesToolBar().actions():
            if action.objectName() == 'ActionSelection':
                self.qgisSelectionToolButton = action.defaultWidget()
                break
        
        self.selectionToolButton.addActions(
            self.qgisSelectionToolButton.actions())
        
        self.selectionToolButton.setDefaultAction(
            self.qgisSelectionToolButton.defaultAction())
        
        self.addWidget(self.selectionToolButton)
        
        for action in self.iface.attributesToolBar().actions(): 
            if action.objectName() == 'mActionDeselectAll':
                self.deselectAllAction = action
                break
        
        self.addAction(self.deselectAllAction)
        
        self.openTableAction = self.iface.actionOpenTable()
        self.addAction(self.openTableAction)
    
    def _set_icon_size(self):
        """Sets icon size according to current QGIS settings."""
        
        self.setIconSize(self.iface.mainWindow().iconSize())
    
    def _set_default_action_selectToolButton(self):
        """Sets selectToolButton's default action."""
        
        self.selectToolButton.setDefaultAction(
            self.qgisSelectToolButton.defaultAction())
    
    def _set_default_action_measureToolButton(self):
        """Sets measureToolButton's default action."""
        
        self.measureToolButton.setDefaultAction(
            self.qgisMeasureToolButton.defaultAction())

