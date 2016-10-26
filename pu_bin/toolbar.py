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
        self.loadVfkAction.setCheckable(True)
        loadVfkIcon = QIcon()
        loadVfkIcon.addPixmap(QPixmap(':/db.png'))
        self.loadVfkAction.setIcon(loadVfkIcon)
        self.openTabActionGroup.addAction(self.loadVfkAction)
        self.addAction(self.loadVfkAction)
        self.loadVfkAction.trigger()
        
        self.checkAction = QAction(self)
        self.checkAction.setObjectName(u'checkAction')
        self.checkAction.setCheckable(True)
        checkIcon = QIcon()
        checkIcon.addPixmap(QPixmap(':/check.png'))
        self.checkAction.setIcon(checkIcon)
        self.openTabActionGroup.addAction(self.checkAction)
        self.addAction(self.checkAction)
        
        self.addSeparator()
        
        self.selectToolButton = QToolButton(self)
        self.selectToolButton.setPopupMode(1)
        
        self.selectRectangleAction = self.iface.actionSelectRectangle()
        self.selectRectangleAction.setObjectName(u'selectRectangleAction')
        self.selectToolButton.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = self.iface.actionSelectPolygon()
        self.selectPolygonAction.setObjectName(u'selectPolygonAction')
        self.selectToolButton.addAction(self.selectPolygonAction)
        
        self.selectFreehandAction = self.iface.actionSelectFreehand()
        self.selectFreehandAction.setObjectName(u'selectFreehandAction')
        self.selectToolButton.addAction(self.selectFreehandAction)
        
        self.selectRadiusAction = self.iface.actionSelectRadius()
        self.selectRadiusAction.setObjectName(u'selectRadiusAction')
        self.selectToolButton.addAction(self.selectRadiusAction)
        
        for action in self.iface.attributesToolBar().actions():
            if action.objectName() == 'ActionSelect':
                self.qgisSelectToolButton = action.defaultWidget()
                break
        
        self.selectToolButton.setDefaultAction(
            self.qgisSelectToolButton.defaultAction())
        
        self.qgisSelectToolButton.toggled.connect(
            self._set_default_action_selectToolButton)
        
        self.insertWidget(
            self.qgisSelectToolButton.defaultAction(),
            self.selectToolButton)
        
        for action in self.iface.attributesToolBar().actions(): 
            if action.objectName() == 'mActionDeselectAll':
                self.deselectAllAction = action
                break
        
        self.addAction(self.deselectAllAction)
    
    def _set_default_action_selectToolButton(self):
        """Sets selectToolButton's default action."""
        
        self.selectToolButton.setDefaultAction(
            self.qgisSelectToolButton.defaultAction())

