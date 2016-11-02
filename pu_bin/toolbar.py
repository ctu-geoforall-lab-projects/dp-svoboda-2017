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

from PyQt4.QtGui import (QToolBar, QToolButton, QAction, QIcon, QPixmap,
                         QActionGroup)

from qgis.core import *


class Toolbar(QToolBar):
    """A widget which contains tools."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        super(QToolBar, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'toolBar')
        self.setIconSize(self.iface.mainWindow().iconSize())
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.openTabActionGroup = QActionGroup(self)
        
        self.loadVfkAction = QAction(self)
        self.loadVfkAction.setObjectName(u'loadVfkAction')
        self.loadVfkAction.setToolTip(u'Načtení VFK souboru')
        self.loadVfkAction.setCheckable(True)
        loadVfkIcon = QIcon()
        loadVfkIcon.addPixmap(QPixmap(':/db.png'))
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
        
        self.checkAction = QAction(self)
        self.checkAction.setObjectName(u'checkAction')
        self.checkAction.setToolTip(u'Kontroly')
        self.checkAction.setCheckable(True)
        checkIcon = QIcon()
        checkIcon.addPixmap(QPixmap(':/check.png'))
        self.checkAction.setIcon(checkIcon)
        self.openTabActionGroup.addAction(self.checkAction)
        self.addAction(self.checkAction)
        
        self.addSeparator()
        
        self.panAction = self.iface.actionPan()
        self.addAction(self.panAction)
        
        self.panToSelectedAction = self.iface.actionPanToSelected()
        self.addAction(self.panToSelectedAction)
        
        self.zoomInAction = self.iface.actionZoomIn()
        self.addAction(self.zoomInAction)
        
        self.zoomOutAction = self.iface.actionZoomOut()
        self.addAction(self.zoomOutAction)
        
        self.zoomFullExtentAction = self.iface.actionZoomFullExtent()
        self.addAction(self.zoomFullExtentAction)
        
        self.zoomToSelectedAction = self.iface.actionZoomToSelected()
        self.addAction(self.zoomToSelectedAction)
        
        self.zoomToLayerAction = self.iface.actionZoomToLayer()
        self.addAction(self.zoomToLayerAction)
        
        self.zoomLastAction = self.iface.actionZoomLast()
        self.addAction(self.zoomLastAction)
        
        self.zoomNextAction = self.iface.actionZoomNext()
        self.addAction(self.zoomNextAction)
        
        self.drawAction = self.iface.actionDraw()
        self.addAction(self.drawAction)
        
        self.addSeparator()
        
        self.identifyAction = self.iface.actionIdentify()
        self.addAction(self.identifyAction)
        
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
        
        self.insertWidget(
            self.qgisSelectToolButton.defaultAction(),
            self.selectToolButton)
        
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
        
        self.insertWidget(
            self.qgisSelectionToolButton.defaultAction(),
            self.selectionToolButton)
        
        for action in self.iface.attributesToolBar().actions(): 
            if action.objectName() == 'mActionDeselectAll':
                self.deselectAllAction = action
                break
        
        self.addAction(self.deselectAllAction)
        
        self.openTableAction = self.iface.actionOpenTable()
        self.addAction(self.openTableAction)
        
        self.openFieldCalculatorAction = self.iface.actionOpenFieldCalculator()
        self.addAction(self.openFieldCalculatorAction)
        
        for action in self.iface.attributesToolBar().actions(): 
            if action.objectName() == 'mActionStatisticalSummary':
                self.statisticalSummaryAction = action
                break
        
        self.addAction(self.statisticalSummaryAction)
        
        self.measureToolButton = QToolButton(self)
        self.measureToolButton.setObjectName(u'measureToolButton')
        self.measureToolButton.setPopupMode(1)
        
        self.measureAction = self.iface.actionMeasure()
        self.measureToolButton.addAction(self.measureAction)
        
        self.measureAreaAction = self.iface.actionMeasureArea()
        self.measureToolButton.addAction(self.measureAreaAction)
        
        for action in self.iface.attributesToolBar().actions():
            if action.objectName() == 'ActionMeasure':
                self.qgisMeasureToolButton = action.defaultWidget()
                break
        
        for action in self.qgisMeasureToolButton.actions():
            if action.objectName() == 'mActionMeasureAngle':
                self.measureAngleAction = action
                break
        
        self.measureToolButton.addAction(self.measureAngleAction)
        
        self.qgisMeasureToolButton.toggled.connect(
            self._set_default_action_measureToolButton)
        
        self._set_default_action_measureToolButton()
        
        self.insertWidget(
            self.qgisMeasureToolButton.defaultAction(),
            self.measureToolButton)
    
    def _set_default_action_selectToolButton(self):
        """Sets selectToolButton's default action."""
        
        self.selectToolButton.setDefaultAction(
            self.qgisSelectToolButton.defaultAction())
    
    def _set_default_action_measureToolButton(self):
        """Sets measureToolButton's default action."""
        
        self.measureToolButton.setDefaultAction(
            self.qgisMeasureToolButton.defaultAction())

