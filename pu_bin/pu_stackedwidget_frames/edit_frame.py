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
    
    set_text_statusbar = pyqtSignal(str, int)
    
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
        
        self.set_text_statusbar.connect(self.dW.statusBar.set_text_statusbar)
        
        self.editGridLayout = QGridLayout(self)
        self.editGridLayout.setObjectName(u'editGridLayout')
        self.editGridLayout.setColumnStretch(1, 1)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.editToolBar = QToolBar(self)
        self.editToolBar.setObjectName(u'editToolBar')
        self._set_icon_size()
        self.iface.initializationCompleted.connect(self._set_icon_size)
        self.editGridLayout.addWidget(self.editToolBar, 0, 0, 1, 3)
        
        for action in self.iface.advancedDigitizeToolBar().actions(): 
            if action.objectName() == 'mActionUndo':
                self.undoAction = action
            if action.objectName() == 'mActionRedo':
                self.redoAction = action
        
        self.editToolBar.addAction(self.undoAction)
        
        self.editToolBar.addAction(self.redoAction)
        
        self.editToolBar.addSeparator()
        
        self.toggleEditingAction = self.iface.actionToggleEditing()
        self.toggleEditingAction.setObjectName(u'toggleEditingAction')
        self.editToolBar.addAction(self.toggleEditingAction)
        
        self.saveActiveLayerEditsAction = \
            self.iface.actionSaveActiveLayerEdits()
        self.saveActiveLayerEditsAction.setObjectName(
            u'saveActiveLayerEditsAction')
        self.editToolBar.addAction(self.saveActiveLayerEditsAction)
        
        self.cancelEditsAction = self.iface.actionCancelEdits()
        self.cancelEditsAction.setObjectName(u'cancelEditsAction')
        self.editToolBar.addAction(self.cancelEditsAction)
        
        self.addFeatureAction = self.iface.actionAddFeature()
        self.addFeatureAction.setObjectName(u'addFeatureAction')
        self.editToolBar.addAction(self.addFeatureAction)
        
        self.moveFeatureAction = self.iface.actionMoveFeature()
        self.moveFeatureAction.setObjectName(u'moveFeatureAction')
        self.editToolBar.addAction(self.moveFeatureAction)
        
        self.nodeToolAction = self.iface.actionNodeTool()
        self.nodeToolAction.setObjectName(u'nodeToolAction')
        self.editToolBar.addAction(self.nodeToolAction)
        
        self.deleteSelectedAction = self.iface.actionDeleteSelected()
        self.deleteSelectedAction.setObjectName(u'deleteSelectedAction')
        self.editToolBar.addAction(self.deleteSelectedAction)
        
        self.splitFeaturesAction = self.iface.actionSplitFeatures()
        self.splitFeaturesAction.setObjectName(u'splitFeaturesAction')
        self.editToolBar.addAction(self.splitFeaturesAction)
        
        self.perimeterLabel = QLabel(self)
        self.perimeterLabel.setObjectName(u'perimeterLabel')
        self.perimeterLabel.setText(u'Obvod:')
        self.editGridLayout.addWidget(self.perimeterLabel, 1, 0, 1, 1)
        
        self.perimeterMapLayerComboBox = QgsMapLayerComboBox(self)
        self.perimeterMapLayerComboBox.setObjectName(
            u'perimeterMapLayerComboBox')
        self.perimeterMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.perimeterMapLayerComboBox.layerChanged.connect(
            self._connect_perimeter_map_layer_combo_box)
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
        self.categoryComboBox.addItem(u'mimo obvod')
        self.categoryComboBox.addItem(u'v obvodu - neřešené')
        self.categoryComboBox.addItem(u'v obvodu - řešené')
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
            self._start_setting_pu_category)
        self.editGridLayout.addWidget(self.setCategoryPushButton, 4, 2, 1, 1)
    
    def _set_icon_size(self):
        """Sets editToolBar icon size according to current QGIS settings."""
        
        self.editToolBar.setIconSize(self.iface.mainWindow().iconSize())
    
    
    def _set_categoryValue(self):
        """Sets categoryValue according to the current index.
        
        categoryValue - description:
            0 - mimo obvod
            1 - v obvodu - neřešené
            2 - v obvodu - řešené
        
        """
        
        self.categoryValue = self.categoryComboBox.currentIndex()
    
    def _connect_perimeter_map_layer_combo_box(self):
        """Connects to perimeterMapLayerComboBox in perimeterWidget."""
        
        layer = self.perimeterMapLayerComboBox.currentLayer()
        
        self.dW.stackedWidget.checkAnalysisFrame.\
            perimeterWidget.perimeterMapLayerComboBox.setLayer(layer)
    
    def _create_perimeter(self):
        """Creates a perimeter layer from the active layer."""
        
        try:
            succes, layer = self.dW.check_layer(self)
            
            if not succes == True:
                return
            
            editing = self.dW.check_editing()
            
            title = u'Uložit vrstvu obvodu jako...'
            filters = u'.shp (*.shp)'
            
            filePath = self.dW.open_file_dialog(title, filters, False)
            
            if filePath:
                selectedFeaturesIDs = layer.selectedFeaturesIds()
                
                self.dW.select_features_by_field_value(
                    layer, self.categoryName, 1)
                
                featuresCount = layer.selectedFeatureCount()
                
                fileInfo = QFileInfo(filePath)
                
                if not fileInfo.suffix() == u'shp':
                    filePath = fileInfo.absoluteFilePath() + u'.shp'
                    fileInfo = QFileInfo(filePath)
                
                if u'pu.shp' not in fileInfo.completeSuffix():
                    filePath = QDir(fileInfo.absolutePath()).\
                        filePath(fileInfo.completeBaseName() + u'.pu.shp')
                
                perimeterPath = processing.runalg(
                    'qgis:dissolve',
                    layer, False, self.categoryName, filePath)['OUTPUT']
                
                layer.selectByIds(selectedFeaturesIDs)
                
                fileInfo = QFileInfo(filePath)
                
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
                
                self.set_text_statusbar.emit(
                    u'Obvod byl úspešně vytvořen.', 15)
        except:
            self.dW.display_error_messages(
                u'Error creating perimeter.',
                u'Chyba při vytváření obvodu.')
        
    def _start_setting_pu_category(self):
        """Starts setting PU category in a separate thread.."""
        
        succes, layer = self.dW.check_layer(self)
        
        if not succes == True:
            return
        
        self.executeThread = Executehread(layer)
        self.executeThread.work.connect(self._run_setting_pu_category)
        self.executeThread.start()
    
    def _run_setting_pu_category(self, layer):
        """Calls methods for setting PU category.
        
        When selectedRadioButton is checked it sets a categoryValue
        to categoryName column for selected features.
        
        When perimeterRadioButton is checked it sets a categoryValue
        to categoryName column for all features according to current layer
        in perimeterMapLayerComboBox.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        """
        try:
            perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
            
            perimeterLayerCrs = perimeterLayer.crs().authid()
            layerCrs = layer.crs().authid()
            
            if perimeterLayerCrs != layerCrs:
                self.set_text_statusbar.emit(
                    u'Aktivní vrstva a vrstva obvodu nemají stejný '
                    u'souřadnicový systém.', 10)
                return
            
            editing = self.dW.check_editing()
            
            if self.selectedRadioButton.isChecked():
                self._set_pu_category_for_selected(layer, perimeterLayer)
            
            if self.perimeterRadioButton.isChecked():
                self._set_pu_category_by_perimeter(layer, perimeterLayer)
            
            if editing == True:
                self.toggleEditingAction.trigger()
        except:
            self.dW.display_error_messages(
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
            self.set_text_statusbar.emit(
                u'V aktivní vrstvě nejsou vybrány žádné prvky.', 10)
            return
        
        currentCategory = self.categoryComboBox.currentText()
        
        if featuresCount == 1:
            self.set_text_statusbar.emit(
                u'Zařazuji vybranou parcelu do kategorie "{}".'
                .format(currentCategory), 0)
        else:
            self.set_text_statusbar.emit(
                u'Zařazuji vybrané parcely do kategorie "{}".'
                .format(currentCategory), 0)
        
        tempCategoryValue = self.categoryValue
        
        selectedFeaturesIDs = layer.selectedFeaturesIds()
        
        selectedFeatures = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, selectedFeatures, self.categoryName, tempCategoryValue)
        
        layer.selectByIds(selectedFeaturesIDs)
        
        selectedFeatures = layer.selectedFeaturesIterator()
        
        perimeterLayerPath = perimeterLayer.source()
        perimeterLayerName = perimeterLayer.name()
        perimeterLayerFeatureCount = perimeterLayer.featureCount()
        
        tempPerimeterLayerName = perimeterLayerName + u'.pu.temp'
        
        if perimeterLayerFeatureCount == 0 or tempCategoryValue in (2, 3):
            tempPerimeterLayer = self._create_temp_polygon_layer(
                layer, tempPerimeterLayerName)
            
            QgsMapLayerRegistry.instance().addMapLayer(tempPerimeterLayer)
        else:
            tempPerimeterPath = processing.runalg(
                'qgis:dissolve', perimeterLayer, True, None, None)['OUTPUT']
            
            tempPerimeterLayer = QgsVectorLayer(
                tempPerimeterPath, tempPerimeterLayerName, 'ogr')
        
        QgsApplication.processEvents()
        
        tempPerimeterLayer.startEditing()
        tempPerimeterLayer.updateFields()
        
        for feature in selectedFeatures:
            copiedFeature = QgsFeature(tempPerimeterLayer.pendingFields())
            copiedFeature.setGeometry(feature.geometry())
            tempPerimeterLayer.addFeature(copiedFeature)
        
        tempPerimeterLayer.commitChanges()
        
        perimeterFileInfo = QFileInfo(perimeterLayerPath)
        
        if u'pu.shp' not in perimeterFileInfo.completeSuffix():
            newPerimeterPath = QDir(perimeterFileInfo.absolutePath()).\
                filePath(perimeterFileInfo.completeBaseName() + u'.pu.shp')
            newPerimeterLayerName = perimeterLayerName + u'.pu'
            
            loadedLayer = False
        else:
            newPerimeterPath = perimeterFileInfo.absoluteFilePath()
            newPerimeterLayerName = perimeterLayerName
            
            loadedLayer = True
        
        if tempCategoryValue in (2, 3):
            processing.runalg(
                'qgis:difference',
                perimeterLayer, tempPerimeterLayer, False, newPerimeterPath)
        else:
            processing.runalg(
                'qgis:dissolve',
                tempPerimeterLayer, True, None, newPerimeterPath)
        
        QgsApplication.processEvents()
        
        QgsMapLayerRegistry.instance().removeMapLayer(tempPerimeterLayer)
        
        if loadedLayer:
            self.iface.actionDraw().trigger()
        else:
            newPerimeterLayer = QgsVectorLayer(
                newPerimeterPath, newPerimeterLayerName, 'ogr')
            
            if newPerimeterLayer.isValid():
                style = ':/perimeter.qml'
                newPerimeterLayer.loadNamedStyle(style)
                QgsMapLayerRegistry.instance().addMapLayer(newPerimeterLayer)
            
            self.perimeterMapLayerComboBox.setLayer(newPerimeterLayer)
    
        self.iface.setActiveLayer(layer)
        
        if featuresCount == 1:
            self.set_text_statusbar.emit(
                u'Vybraná parcela byla zařazena do kategorie "{}".'
                .format(currentCategory), 20)
        else:
            self.set_text_statusbar.emit(
                u'Vybrané parcely byly zařazeny do kategorie "{}".'
                .format(currentCategory), 20)
    
    def _create_temp_polygon_layer(self, layer, tempPolygonLayerName):
        """Creates a temporary polygon layer.
        
        Creates a temporary polygon layer with the same CRS as the input layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the input layer.
            tempPolygonLayerName (str): A name of the temporary layer.
        
        Returns:
            QgsVectorLayer: A reference to the temporary polygon layer.
        
        """
        
        layerCrs = layer.crs().authid()
        
        tempPolygonLayer = QgsVectorLayer(
            'Polygon?crs=' + layerCrs,
            tempPolygonLayerName,
            'memory')
        
        return tempPolygonLayer
    
    def _set_pu_category_by_perimeter(self, layer, perimeterLayer):
        """Sets a categoryValue to categoryName column for all features
        according to current layer in perimeterMapLayerComboBox.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
        self.set_text_statusbar.emit(u'Zařazuji parcely na základě obvodu.', 0)
        
        selectedFeaturesIDs = layer.selectedFeaturesIds()
        
        processing.runalg(
            'qgis:selectbylocation', layer, perimeterLayer, u'within', 0, 0)
        
        features = layer.selectedFeaturesIterator()
        
        layer.startEditing()
        
        self.dW.set_field_value_for_features(
            layer, features, self.categoryName, 1, False)
        
        layer.invertSelection()
        
        features = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, features, self.categoryName, 2, False)
        
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
            layer, features, self.categoryName, 3, False)
        
        layer.commitChanges()
        
        layer.selectByIds(selectedFeaturesIDs)
        
        self.set_text_statusbar.emit(
            u'Zařazení parcel na základě obvodu úspěšně dokončeno.', 30)
        
    def _select_category(self):
        """Selects features in current category."""
        
        try:
            succes, layer = self.dW.check_layer(self)
            
            if not succes == True:
                return
            
            self.dW.select_features_by_field_value(
                layer, self.categoryName, self.categoryValue)
            
            currentCategory = self.categoryComboBox.currentText()
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featuresCount == 0:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" není žádná parcela.'
                    .format(currentCategory), duration)
            elif featuresCount == 1:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" je {} parcela.'
                    .format(currentCategory, featuresCount), duration)
            elif 1 < featuresCount < 5:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" jsou {} parcely.'
                    .format(currentCategory, featuresCount), duration)
            elif 5 <= featuresCount:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" je {} parcel.'
                    .format(currentCategory, featuresCount), duration)
        except:
            self.dW.display_error_messages(
                u'Error selecting parcels in category.',
                u'Chyba při vybírání parcel v kategorii.')

