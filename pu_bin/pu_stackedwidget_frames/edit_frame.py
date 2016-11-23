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
                         QPixmap, QMenu, QHBoxLayout, QLabel, QComboBox,
                         QPushButton)
from PyQt4.QtCore import pyqtSignal, QSignalMapper

from qgis.core import *

from execute_thread import Executehread


class EditFrame(QFrame):
    """A frame which contains widgets for editing."""
    
    text_statusbar = pyqtSignal(str, int)
    
    def __init__(self, parentWidget, dockWidgetName, iface, dockWidget):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
            dockWidget (QWidget): A reference to the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        self.dW = dockWidget
        
        super(EditFrame, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.categoryValue = 1
        self.categoryName = 'PU_KATEGORIE'
        
        self.setObjectName(u'editFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.text_statusbar.connect(self.dW.statusbar._set_text_statusbar)
        
        self.editGridLayout = QGridLayout(self)
        self.editGridLayout.setObjectName(u'editGridLayout')
        self.editGridLayout.setColumnStretch(0, 1)
        self.editGridLayout.setColumnStretch(1, 1)
        
        self.setPuCategorySignalMapper = QSignalMapper(self)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.editToolbar = QToolBar(self)
        self.editToolbar.setObjectName(u'editToolbar')
        self.editToolbar.setIconSize(self.iface.mainWindow().iconSize())
        self.editGridLayout.addWidget(self.editToolbar, 0, 0, 1, 2)
        
        self.allEditsToolButton = QToolButton(self)
        self.allEditsToolButton.setObjectName(u'allEditsToolButton')
        self.allEditsToolButton.setPopupMode(2)
        self.editToolbar.addWidget(self.allEditsToolButton)
        
        for action in self.iface.digitizeToolBar().actions():
            if action.objectName() == 'mActionAllEdits':
                self.qgisAllEditsAction = action
                break
        
        self.allEditsToolButton.setIcon(self.qgisAllEditsAction.icon())
        self.allEditsToolButton.setToolTip(self.qgisAllEditsAction.toolTip())
        
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
        
        self.categoryHBoxLayout = QHBoxLayout(self)
        self.categoryHBoxLayout.setObjectName(u'categoryHBoxLayout')
        self.editGridLayout.addLayout(self.categoryHBoxLayout, 1, 0, 1, 2)
        
        self.categoryLabel = QLabel(self)
        self.categoryLabel.setObjectName(u'categoryLabel')
        self.categoryLabel.setText(u'Kategorie parcel:')
        self.categoryHBoxLayout.addWidget(self.categoryLabel)
        
        self.categoryComboBox = QComboBox(self)
        self.categoryComboBox.setObjectName(u'categoryComboBox')
        self.categoryComboBox.addItem(u'v obvodu - řešené')
        self.categoryComboBox.addItem(u'v obvodu - neřešené')
        self.categoryComboBox.addItem(u'mimo obvod')
        self.categoryComboBox.currentIndexChanged.connect(
            self._set_categoryValue)
        self.categoryHBoxLayout.addWidget(self.categoryComboBox, 1)
        
        self.setCategoryPushButton = QPushButton(self)
        self.setCategoryPushButton.setObjectName(u'setCategoryPushButton')
        self.setCategoryPushButton.setText(u'Zařadit')
        self.setCategoryPushButton.setToolTip(
            u'Zařadit vybrané parcely do kategorie')
        self.setCategoryPushButton.clicked.connect(
            self._run_setting_pu_category)
        self.editGridLayout.addWidget(self.setCategoryPushButton, 2, 0, 1, 1)
        
        self.selectCategoryPushButton = QPushButton(self)
        self.selectCategoryPushButton.setObjectName(u'selectCategoryPushButton')
        self.selectCategoryPushButton.setText(u'Vybrat')
        self.selectCategoryPushButton.setToolTip(u'Vybrat parcely v kategorii')
        self.selectCategoryPushButton.clicked.connect(self._select_category)
        self.editGridLayout.addWidget(self.selectCategoryPushButton, 2, 1, 1, 1)
    
    def _enable_allEditsToolButton(self):
        """Enables or disables qgisAllEditsAction.
        
        Enables or disables qgisAllEditsAction according to
        QGIS mActionAllEdits.
        
        """
        
        if self.qgisAllEditsAction.isEnabled():
            self.allEditsToolButton.setEnabled(True)
        else:
            self.allEditsToolButton.setDisabled(True)
    
    def _set_categoryValue(self):
        """Sets categoryValue according to the current index."""
        
        self.categoryValue = self.categoryComboBox.currentIndex() + 1
        
    def _run_setting_pu_category(self):
        """Calls method for setting a categoryValue to categoryName column."""
        
        succes, layer = self.pW.check_active_layer(self)
        
        if not succes == True:
            return
        
        self.executeThread = Executehread(layer)
        self.executeThread.work.connect(self._set_pu_category)
        self.executeThread.start()
    
    def _set_pu_category(self, layer):
        """Sets a categoryValue to categoryName column for selected features.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        """
        try:
            editing = self.dW.stackedWidget.check_editing()
            
            featuresCount = layer.selectedFeatureCount()
            
            if featuresCount == 0:
                self.text_statusbar.emit(
                    u'V aktivní vrstvě nejsou vybrány žádné prvky.', 7000)
                return
            
            currentCategory = self.categoryComboBox.currentText()
            
            if featuresCount == 1:
                self.text_statusbar.emit(
                    u'Zařazuji vybranou parcelu do kategorie "{}".'
                    .format(currentCategory), 0)
            else:
                self.text_statusbar.emit(
                    u'Zařazuji vybrané parcely do kategorie "{}".'
                    .format(currentCategory), 0)
            
            fieldID = layer.fieldNameIndex(self.categoryName)
            
            layer.startEditing()
            layer.updateFields()
            
            selectedFeatures = layer.selectedFeatures()
            
            for feature in selectedFeatures:
                if feature.attribute(self.categoryName) != self.categoryValue:
                    featureID = feature.id()
                    layer.changeAttributeValue(
                        featureID, fieldID, self.categoryValue)
            
            layer.commitChanges()
            
            if editing == True:
                self.toggleEditingAction.trigger()
            
            self.text_statusbar.emit(
                u'Vybrané parcely byly zařazeny do kategorie "{}".'
                .format(currentCategory), 7000)
        except:
            self.dW._raise_pu_error(
                u'Error setting parcel category.',
                u'Chyba při zařazování do kategorie parcel.')
    
    def _select_category(self):
        """Selects features in current category."""
        
        try:
            succes, layer = self.pW.check_active_layer(self)
            
            if not succes == True:
                return
    
            fieldID = layer.fieldNameIndex(self.categoryName)
                    
            expression = QgsExpression(
                "\"{}\"={}".format(self.categoryName, self.categoryValue))
            
            features = layer.getFeatures(QgsFeatureRequest(expression))
            
            featuresID = [feature.id() for feature in features]
            
            layer.selectByIds(featuresID)
            
            currentCategory = self.categoryComboBox.currentText()
            
            featuresCount = len(featuresID)
            
            duration = 10000
            
            if featuresCount == 0:
                self.text_statusbar.emit(
                    u'V kategorii "{}" není žádná parcela.'
                    .format(currentCategory), duration)
            elif featuresCount == 1:
                self.text_statusbar.emit(
                    u'V kategorii "{}" je {} parcela.'
                    .format(currentCategory, featuresCount), duration)
            elif 1 < featuresCount < 5:
                self.text_statusbar.emit(
                    u'V kategorii "{}" jsou {} parcely.'
                    .format(currentCategory, featuresCount), duration)
            elif 5 <= featuresCount:
                self.text_statusbar.emit(
                    u'V kategorii "{}" je {} parcel.'
                    .format(currentCategory, featuresCount), duration)
        except:
            self.dW._raise_pu_error(
                u'Error selecting parcels in category.',
                u'Chyba při vybírání parcel v kategorii.')

