# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EditFrame
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

from PyQt4.QtGui import (QFrame, QGridLayout, QToolBar, QToolButton, QIcon,
                         QPixmap, QMenu)


class EditFrame(QFrame):
    """A frame which contains widgets for editing."""
    
    def __init__(self, parentWidget, dockWidgetName, iface, dockWidget):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            dockWidget (QWidget): A reference to the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        self.dW = dockWidget
        
        super(QFrame, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'editFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.editGridLayout = QGridLayout(self)
        self.editGridLayout.setObjectName(u'editGridLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.editToolbar = QToolBar(self)
        self.editToolbar.setObjectName(u'editToolbar')
        self.editToolbar.setIconSize(self.iface.mainWindow().iconSize())
        self.editGridLayout.addWidget(self.editToolbar, 0, 0, 1, 1)
        
        self.allEditsToolButton = QToolButton(self)
        self.allEditsToolButton.setObjectName(u'allEditsToolButton')
        self.allEditsToolButton.setPopupMode(2)
        allEditsIcon = QIcon()
        allEditsIcon.addPixmap(QPixmap(':/allEditsAction.svg'))
        self.allEditsToolButton.setIcon(allEditsIcon)
        
        for action in self.iface.digitizeToolBar().actions():
            if action.objectName() == 'mActionAllEdits':
                self.qgisAllEditsAction = action
                break
        
        self.qgisAllEditsAction.changed.connect(self._enable_allEditsToolButton)
        
        self._enable_allEditsToolButton()
        
        self.allEditsMenu = QMenu(self)
        
        self.saveEditsAction = self.iface.actionSaveEdits()
        self.saveEditsAction.setObjectName(u'saveEditsAction')
        self.allEditsMenu.addAction(self.saveEditsAction)
        
        self.rollbackEditsAction = self.iface.actionRollbackEdits()
        self.rollbackEditsAction.setObjectName(u'rollbackEditsAction')
        self.allEditsMenu.addAction(self.rollbackEditsAction)
        
        self.cancelEditsAction = self.iface.actionCancelEdits()
        self.cancelEditsAction.setObjectName(u'cancelEditsAction')
        self.allEditsMenu.addAction(self.cancelEditsAction)
        
        self.allEditsMenu.addSeparator()
        
        self.saveAllEditsAction = self.iface.actionSaveAllEdits()
        self.saveAllEditsAction.setObjectName(u'saveAllEditsAction')
        self.allEditsMenu.addAction(self.saveAllEditsAction)
        
        self.rollbackAllEditsAction = self.iface.actionRollbackAllEdits()
        self.rollbackAllEditsAction.setObjectName(u'rollbackAllEditsAction')
        self.allEditsMenu.addAction(self.rollbackAllEditsAction)
        
        self.cancelAllEditsAction = self.iface.actionCancelAllEdits()
        self.cancelAllEditsAction.setObjectName(u'cancelAllEditsAction')
        self.allEditsMenu.addAction(self.cancelAllEditsAction)
        
        self.allEditsToolButton.setMenu(self.allEditsMenu)
        
        self.editToolbar.addWidget(self.allEditsToolButton)
        
        self.toggleEditingAction = self.iface.actionToggleEditing()
        self.toggleEditingAction.setObjectName(u'toggleEditingAction')
        self.editToolbar.addAction(self.toggleEditingAction)
        
        self.saveActiveLayerEditsAction = self.iface\
            .actionSaveActiveLayerEdits()
        self.saveActiveLayerEditsAction.setObjectName(
            u'saveActiveLayerEditsAction')
        self.editToolbar.addAction(self.saveActiveLayerEditsAction)
        
        self.addFeatureAction = self.iface.actionAddFeature()
        self.addFeatureAction.setObjectName(u'addFeatureAction')
        self.editToolbar.addAction(self.addFeatureAction)
        
        self.moveFeatureAction = self.iface.actionMoveFeature()
        self.moveFeatureAction.setObjectName(u'moveFeatureAction')
        self.editToolbar.addAction(self.moveFeatureAction)
        
        self.nodeToolAction = self.iface.actionNodeTool()
        self.nodeToolAction.setObjectName(u'nodeToolAction')
        self.editToolbar.addAction(self.nodeToolAction)
        
        self.deleteSelectedAction = self.iface.actionDeleteSelected()
        self.deleteSelectedAction.setObjectName(u'deleteSelectedAction')
        self.editToolbar.addAction(self.deleteSelectedAction)
        
        self.cutFeaturesAction = self.iface.actionCutFeatures()
        self.cutFeaturesAction.setObjectName(u'cutFeaturesAction')
        self.editToolbar.addAction(self.cutFeaturesAction)
        
        self.copyFeaturesAction = self.iface.actionCopyFeatures()
        self.copyFeaturesAction.setObjectName(u'copyFeaturesAction')
        self.editToolbar.addAction(self.copyFeaturesAction)
        
        self.pasteFeaturesAction = self.iface.actionPasteFeatures()
        self.pasteFeaturesAction.setObjectName(u'pasteFeaturesAction')
        self.editToolbar.addAction(self.pasteFeaturesAction)
    
    def _enable_allEditsToolButton(self):
        if self.qgisAllEditsAction.isEnabled():
            self.allEditsToolButton.setEnabled(True)
        else:
            self.allEditsToolButton.setDisabled(True)

