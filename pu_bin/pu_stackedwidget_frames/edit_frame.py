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
                         QPixmap, QMenu, QLabel, QComboBox, QPushButton,
                         QHBoxLayout, QRadioButton)
from PyQt4.QtCore import pyqtSignal, QFileInfo, QDir

from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel
from qgis.core import *

import processing

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
        
        self.text_statusbar.connect(self.dW.statusbar.set_text_statusbar)
        
        self.editGridLayout = QGridLayout(self)
        self.editGridLayout.setObjectName(u'editGridLayout')
        self.editGridLayout.setColumnStretch(1, 1)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.editToolbar = QToolBar(self)
        self.editToolbar.setObjectName(u'editToolbar')
        self.editToolbar.setIconSize(self.iface.mainWindow().iconSize())
        self.editGridLayout.addWidget(self.editToolbar, 0, 0, 1, 3)
        
        for action in self.iface.advancedDigitizeToolBar().actions(): 
            if action.objectName() == 'mActionUndo':
                self.undoAction = action
            if action.objectName() == 'mActionRedo':
                self.redoAction = action
        
        self.editToolbar.addAction(self.undoAction)
        
        self.editToolbar.addAction(self.redoAction)
        
        self.editToolbar.addSeparator()
        
        self.toggleEditingAction = self.iface.actionToggleEditing()
        self.toggleEditingAction.setObjectName(u'toggleEditingAction')
        self.editToolbar.addAction(self.toggleEditingAction)
        
        self.saveActiveLayerEditsAction = \
            self.iface.actionSaveActiveLayerEdits()
        self.saveActiveLayerEditsAction.setObjectName(
            u'saveActiveLayerEditsAction')
        self.editToolbar.addAction(self.saveActiveLayerEditsAction)
        
        self.cancelEditsAction = self.iface.actionCancelEdits()
        self.cancelEditsAction.setObjectName(u'cancelEditsAction')
        self.editToolbar.addAction(self.cancelEditsAction)
        
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
        
        self.splitFeaturesAction = self.iface.actionSplitFeatures()
        self.splitFeaturesAction.setObjectName(u'splitFeaturesAction')
        self.editToolbar.addAction(self.splitFeaturesAction)
        
        self.perimeterLabel = QLabel(self)
        self.perimeterLabel.setObjectName(u'perimeterLabel')
        self.perimeterLabel.setText(u'Obvod:')
        self.editGridLayout.addWidget(self.perimeterLabel, 1, 0, 1, 1)
        
        self.perimeterMapLayerComboBox = QgsMapLayerComboBox(self)
        self.perimeterMapLayerComboBox.setObjectName(
            u'perimeterMapLayerComboBox')
        self.perimeterMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.editGridLayout.addWidget(
            self.perimeterMapLayerComboBox, 1, 1, 1, 1)
        
        self.createPerimeterPushButton = QPushButton(self)
        self.createPerimeterPushButton.setObjectName(
            u'createPerimeterPushButton')
        self.createPerimeterPushButton.setText(u'Vytvořit')
        self.createPerimeterPushButton.setToolTip(
            u'Vytvořit vrstvu obvodu (.shp) z aktivní vrstvy a načíst')
        self.createPerimeterPushButton.clicked.connect(self._create_perimeter)
        self.editGridLayout.addWidget(
            self.createPerimeterPushButton, 1, 2, 1, 1)
        
        self.categoryLabel = QLabel(self)
        self.categoryLabel.setObjectName(u'categoryLabel')
        self.categoryLabel.setText(u'Kategorie parcel:')
        self.editGridLayout.addWidget(self.categoryLabel, 2, 0, 1, 1)
        
        self.categoryComboBox = QComboBox(self)
        self.categoryComboBox.setObjectName(u'categoryComboBox')
        self.categoryComboBox.addItem(u'v obvodu - řešené')
        self.categoryComboBox.addItem(u'v obvodu - neřešené')
        self.categoryComboBox.addItem(u'mimo obvod')
        self.categoryComboBox.currentIndexChanged.connect(
            self._set_categoryValue)
        self.editGridLayout.addWidget(self.categoryComboBox, 2, 1, 1, 1)
        
        self.selectCategoryPushButton = QPushButton(self)
        self.selectCategoryPushButton.setObjectName(u'selectCategoryPushButton')
        self.selectCategoryPushButton.setText(u'Zobrazit')
        self.selectCategoryPushButton.setToolTip(
            u'Zobrazit (vybrat) parcely v kategorii')
        self.selectCategoryPushButton.clicked.connect(self._select_category)
        self.editGridLayout.addWidget(self.selectCategoryPushButton, 2, 2, 1, 1)
        
        self.editGridLayout.setRowStretch(3, 1)
        
        self.setCategoryLabel = QLabel(self)
        self.setCategoryLabel.setObjectName(u'setCategoryLabel')
        self.setCategoryLabel.setText(u'Zařadit:')
        self.editGridLayout.addWidget(self.setCategoryLabel, 4, 0, 1, 1)
        
        self.setCategoryHBoxLayout = QHBoxLayout(self)
        self.editGridLayout.addLayout(self.setCategoryHBoxLayout, 4, 1)
        
        self.selectedRadioButton = QRadioButton(self)
        self.selectedRadioButton.setObjectName(u'selectedRadioButton')
        self.selectedRadioButton.setText(u'vybrané parcely')
        self.selectedRadioButton.setToolTip(
            u'Zařadit vybrané parcely do kategorie')
        self.selectedRadioButton.toggle()
        self.setCategoryHBoxLayout.addWidget(self.selectedRadioButton)
        
        self.perimeterRadioButton = QRadioButton(self)
        self.perimeterRadioButton.setObjectName(u'perimeterRadioButton')
        self.perimeterRadioButton.setText(u'obvodem')
        self.perimeterRadioButton.setToolTip(
            u'Rozřadit všechny parcely do kategorií na základě obvodu')
        self.setCategoryHBoxLayout.addWidget(self.perimeterRadioButton)
        
        self.setCategoryPushButton = QPushButton(self)
        self.setCategoryPushButton.setObjectName(u'setCategoryPushButton')
        self.setCategoryPushButton.setText(u'Zařadit')
        self.setCategoryPushButton.clicked.connect(
            self._run_setting_pu_category)
        self.editGridLayout.addWidget(self.setCategoryPushButton, 4, 2, 1, 1)
    
    def _create_perimeter(self):
        """Creates a perimeter layer from the active layer."""
        
        try:
            succes, layer = self.dW.check_active_layer(self)
            
            if not succes == True:
                return
            
            editing = self.dW.check_editing()
            
            title = u'Uložit vrstvu obvodu jako...'
            filters = u'.shp (*.shp)'
            
            filePath = self.dW.open_file_dialog(title, filters, False)
            
            if filePath:
                selectedFeaturesIDs = layer.selectedFeaturesIds()
                
                self.dW.select_features_by_field_and_value(
                    layer, self.categoryName, 1)
                
                featuresCount = layer.selectedFeatureCount()
                
                fileInfo = QFileInfo(filePath)
                
                if not fileInfo.suffix() == u'shp':
                    filePath = fileInfo.absoluteFilePath() + '.shp'
                    fileInfo = QFileInfo(filePath)
                
                if u'pu.shp' not in fileInfo.completeSuffix():
                    filePath = \
                        fileInfo.absolutePath() + \
                        QDir.separator() + \
                        fileInfo.completeBaseName() + \
                        u'.pu.' + \
                        fileInfo.suffix()
                    fileInfo = QFileInfo(filePath)
                
                perimeterPath = processing.runalg(
                    'qgis:dissolve',
                    layer, False, self.categoryName, filePath)['OUTPUT']
                
                layer.selectByIds(selectedFeaturesIDs)
                
                perimeterName = fileInfo.completeBaseName()
                
                perimeterLayer = QgsVectorLayer(
                    perimeterPath, perimeterName, 'ogr')
                
                if featuresCount == 0:
                    perimeterLayer.startEditing()
                    
                    features = perimeterLayer.getFeatures()
                    featuresID = [feature.id() for feature in features]
                    perimeterLayer.deleteFeatures(featuresID)
                    
                    perimeterLayer.commitChanges()
                
                perimeterLayer.startEditing()
                
                fields = layer.pendingFields()
                
                perimeterLayerAttributesIDs = []
                
                for i in perimeterLayer.pendingAllAttributesList():
                    if fields[i].name() == u'rowid':
                        continue
                    perimeterLayerAttributesIDs.append(i)
                
                perimeterLayer.deleteAttributes(perimeterLayerAttributesIDs)
                
                perimeterLayer.updateFields()
                perimeterLayer.commitChanges()
                
                if perimeterLayer.isValid():
                    style = ':/perimeter.qml'
                    perimeterLayer.loadNamedStyle(style)
                    QgsMapLayerRegistry.instance().addMapLayer(perimeterLayer)
                    
                    self.perimeterMapLayerComboBox.setLayer(perimeterLayer)
                
                self.iface.setActiveLayer(layer)
                
                if editing == True:
                    self.toggleEditingAction.trigger()
                
                self.text_statusbar.emit(
                    u'Obvod byl úspešně vytvořen.', 15000)
        except:
            self.dW._display_error_messages(
                u'Error creating perimeter.',
                u'Chyba při vytváření obvodu.')
    
    def _set_categoryValue(self):
        """Sets categoryValue according to the current index."""
        
        self.categoryValue = self.categoryComboBox.currentIndex() + 1
        
    def _run_setting_pu_category(self):
        """Calls method for setting a categoryValue to categoryName column."""
        
        succes, layer = self.dW.check_active_layer(self)
        
        if not succes == True:
            return
        
        self.executeThread = Executehread(layer)
        self.executeThread.work.connect(self._set_pu_category)
        self.executeThread.start()
    
    def _set_pu_category(self, layer):
        """Sets a categoryValue to categoryName column.
        
        When selectedRadioButton is checked it sets a categoryValue
        to categoryName column for selected features.
        
        When perimeterRadioButton is checked it sets a categoryValue
        to categoryName column for all features according to current layer
        in perimeterMapLayerComboBox.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        Raises:
            dw.puError: When something goes wrong.
        
        """
        try:
            perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
            
            if not perimeterLayer.isValid():
                self.text_statusbar.emit(
                    u'Vrstva obvodu není platná.', 7000)
                return
            
            editing = self.dW.check_editing()
            
            if self.selectedRadioButton.isChecked():
                self._set_pu_category_for_selected(layer, perimeterLayer)
            
            if self.perimeterRadioButton.isChecked():
                self._set_pu_category_by_perimeter(layer, perimeterLayer)
            
            if editing == True:
                self.toggleEditingAction.trigger()
        except:
            self.dW._display_error_messages(
                u'Error setting parcel category.',
                u'Chyba při zařazování do kategorie parcel.')
    
    def _set_pu_category_for_selected(self, layer, perimeterLayer):
        """Sets a categoryValue to categoryName column for selected features.
        
        Also adds selected features to the current layer
        in perimeterMapLayerComboBox and executes Dissolve on that layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
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
        
        selectedFeatures = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, selectedFeatures, self.categoryName, self.categoryValue)
        
        perimeterLayerPath = perimeterLayer.source()
        perimeterLayerName = perimeterLayer.name()
        
        tempPerimeterPath = processing.runalg(
            'qgis:dissolve', perimeterLayer, True, None, None)['OUTPUT']
        
        tempPerimeterLayer = QgsVectorLayer(
            tempPerimeterPath, perimeterLayerName + u'.pu.temp', 'ogr')
        
        tempPerimeterLayer.startEditing()
        
        for feature in selectedFeatures:
            copiedFeature = QgsFeature(tempPerimeterLayer.pendingFields())
            copiedFeature.setGeometry(feature.geometry())
            tempPerimeterLayer.addFeature(copiedFeature)
        
        tempPerimeterLayer.commitChanges()
        
        perimeterFileInfo = QFileInfo(perimeterLayerPath)
        
        if u'pu.shp' not in perimeterFileInfo.completeSuffix():
            newPerimeterPath = \
                perimeterFileInfo.absolutePath() + \
                QDir.separator() + \
                perimeterFileInfo.completeBaseName() + \
                u'.pu.shp'
            newPerimeterLayerName = perimeterLayerName + u'.pu'
        else:
            newPerimeterPath = perimeterFileInfo.absoluteFilePath()
            newPerimeterLayerName = perimeterLayerName
            QgsMapLayerRegistry.instance().removeMapLayer(perimeterLayer)
        
        processing.runalg(
            'qgis:dissolve',
            tempPerimeterLayer, True, None, newPerimeterPath)
        
        newPerimeterLayer = QgsVectorLayer(
            newPerimeterPath, newPerimeterLayerName, 'ogr')
        
        if newPerimeterLayer.isValid():
            style = ':/perimeter.qml'
            newPerimeterLayer.loadNamedStyle(style)
            QgsMapLayerRegistry.instance().addMapLayer(newPerimeterLayer)
            
            self.perimeterMapLayerComboBox.setLayer(newPerimeterLayer)
        
        self.iface.setActiveLayer(layer)
        
        if featuresCount == 1:
            self.text_statusbar.emit(
                u'Vybraná parcela byla zařazena do kategorie "{}".'
                .format(currentCategory), 15000)
        else:
            self.text_statusbar.emit(
                u'Vybrané parcely byly zařazeny do kategorie "{}".'
                .format(currentCategory), 15000)
    
    def _set_pu_category_by_perimeter(self, layer, perimeterLayer):
        """Sets a categoryValue to categoryName column for all features
        according to current layer in perimeterMapLayerComboBox.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
        self.text_statusbar.emit(u'Zařazuji parcely na základě obvodu.', 0)
        
        selectedFeaturesIDs = layer.selectedFeaturesIds()
        
        processing.runalg(
            'qgis:selectbylocation', layer, perimeterLayer, u'within', 0, 0)
        
        features = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, features, self.categoryName, 1)
        
        layer.invertSelection()
        
        features = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, features, self.categoryName, 2)
        
        deleteHolesPerimeterPath = processing.runalg(
            'qgis:deleteholes', perimeterLayer, None)['OUTPUT']
        
        deleteHolesPerimeterLayer = QgsVectorLayer(
            deleteHolesPerimeterPath, 'deleteHolesPerimeter', 'ogr')
        
        processing.runalg(
            'qgis:selectbylocation',
            layer, deleteHolesPerimeterLayer, u'within', 0, 0)
        
        layer.invertSelection()
        
        features = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, features, self.categoryName, 3)
        
        layer.selectByIds(selectedFeaturesIDs)
        
        self.text_statusbar.emit(
            u'Zařazení parcel na základě obvodu úspěšně dokončeno.', 30000)
        
    def _select_category(self):
        """Selects features in current category."""
        
        try:
            succes, layer = self.dW.check_active_layer(self)
            
            if not succes == True:
                return
            
            self.dW.select_features_by_field_and_value(
                layer, self.categoryName, self.categoryValue)
            
            currentCategory = self.categoryComboBox.currentText()
            
            featuresCount = layer.selectedFeatureCount()
            
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
            self.dW._display_error_messages(
                u'Error selecting parcels in category.',
                u'Chyba při vybírání parcel v kategorii.')

