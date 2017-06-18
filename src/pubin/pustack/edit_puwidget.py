# -*- coding: utf-8 -*-
"""
/***************************************************************************
 EditPuWidget
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

from PyQt4.QtGui import (QGridLayout, QToolBar, QToolButton, QIcon,
                         QPixmap, QMenu, QLabel, QComboBox, QPushButton)
from PyQt4.QtCore import pyqtSignal, QFileInfo, QDir, Qt, QPyNullVariant

from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel
from qgis.core import *

import processing

from puwidget import PuWidget
from execute_thread import ExecuteThread


class EditPuWidget(PuWidget):
    """A widget for editing."""
    
    set_text_statusbar = pyqtSignal(str, int, bool)
    
    def _setup_self(self):
        """Sets up self."""
        
        self.categoryValue = 0
        self.categoryValues = (0, 1, 2, None)
        self.categoryName = self.dW.puCategoryColumnName
        self.shortCategoryName = self.categoryName[:10]
        self.setCategoryValue = 0
        
        self.setObjectName(u'editFrame')
        
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName(u'gridLayout')
        self.gridLayout.setColumnStretch(1, 1)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.set_text_statusbar.connect(self.dW.statusBar.set_text)
        
        self.lastPerimeterLayer = None
        
        self.editToolBar = QToolBar(self)
        self.editToolBar.setObjectName(u'editToolBar')
        self._set_icon_size()
        self.iface.initializationCompleted.connect(self._set_icon_size)
        self.gridLayout.addWidget(self.editToolBar, 0, 0, 1, 3)
        
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
        
        self.nodeToolAction = self.iface.actionNodeTool()
        self.nodeToolAction.setObjectName(u'nodeToolAction')
        self.editToolBar.addAction(self.nodeToolAction)
        
        self.deleteSelectedAction = self.iface.actionDeleteSelected()
        self.deleteSelectedAction.setObjectName(u'deleteSelectedAction')
        self.editToolBar.addAction(self.deleteSelectedAction)
        
        self.addPartAction = self.iface.actionAddPart()
        self.addPartAction.setObjectName(u'addPartAction')
        self.editToolBar.addAction(self.addPartAction)
        
        self.splitFeaturesAction = self.iface.actionSplitFeatures()
        self.splitFeaturesAction.setObjectName(u'splitFeaturesAction')
        self.editToolBar.addAction(self.splitFeaturesAction)
        
        self.perimeterLabel = QLabel(self)
        self.perimeterLabel.setObjectName(u'perimeterLabel')
        self.perimeterLabel.setText(u'Obvod:')
        self.gridLayout.addWidget(self.perimeterLabel, 1, 0, 1, 1)
        
        self.perimeterMapLayerComboBox = QgsMapLayerComboBox(self)
        self.perimeterMapLayerComboBox.setObjectName(
            u'perimeterMapLayerComboBox')
        self.perimeterMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.perimeterMapLayerComboBox.activated.connect(
            self.sync_perimeter_map_layer_combo_box)
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._rollback_perimeter_layer)
        QgsMapLayerRegistry.instance().layersRemoved.connect(
            self._reset_perimeter_layer)
        self.set_perimeter_layer(self.lastPerimeterLayer)
        self.gridLayout.addWidget(
            self.perimeterMapLayerComboBox, 1, 1, 1, 1)
        
        self.createPerimeterPushButton = QPushButton(self)
        self.createPerimeterPushButton.setObjectName(
            u'createPerimeterPushButton')
        self.createPerimeterPushButton.setText(u'Vytvořit')
        self.createPerimeterPushButton.setToolTip(
            u'Vytvořit vrstvu obvodu (.shp) z aktivní vrstvy a načíst')
        self.createPerimeterPushButton.clicked.connect(self._create_perimeter)
        self.gridLayout.addWidget(
            self.createPerimeterPushButton, 1, 2, 1, 1)
        
        self.gridLayout.setRowStretch(2, 1)
        
        self.categoryLabel = QLabel(self)
        self.categoryLabel.setObjectName(u'categoryLabel')
        self.categoryLabel.setText(u'Kategorie parcel:')
        self.gridLayout.addWidget(self.categoryLabel, 3, 0, 1, 1)
        
        self.categoryComboBox = QComboBox(self)
        self.categoryComboBox.setObjectName(u'categoryComboBox')
        self.categoryComboBox.addItem(u'mimo obvod (0)')
        self.categoryComboBox.addItem(u'v obvodu - neřešené (1)')
        self.categoryComboBox.addItem(u'v obvodu - řešené (2)')
        self.categoryComboBox.addItem(u'bez kategorie')
        self.categoryComboBox.currentIndexChanged.connect(
            self._set_categoryValue)
        self.gridLayout.addWidget(self.categoryComboBox, 3, 1, 1, 1)
        
        self.selectCategoryPushButton = QPushButton(self)
        self.selectCategoryPushButton.setObjectName(u'selectCategoryPushButton')
        self.selectCategoryPushButton.setText(u'Zobrazit')
        self.selectCategoryPushButton.setToolTip(
            u'Zobrazit (vybrat) parcely v kategorii')
        self.selectCategoryPushButton.clicked.connect(self._select_category)
        self.gridLayout.addWidget(self.selectCategoryPushButton, 3, 2, 1, 1)
        
        self.gridLayout.setRowStretch(4, 1)
        
        self.setCategoryLabel = QLabel(self)
        self.setCategoryLabel.setObjectName(u'setCategoryLabel')
        self.setCategoryLabel.setText(u'Zařadit:')
        self.gridLayout.addWidget(self.setCategoryLabel, 5, 0, 1, 1)
        
        self.setCategoryComboBox = QComboBox(self)
        self.setCategoryComboBox.setObjectName(u'setCategoryComboBox')
        self.setCategoryComboBox.addItem(u'vybrané parcely')
        self.setCategoryComboBox.setItemData(
            0, u'Zařadit vybrané parcely do kategorie', Qt.ToolTipRole)
        self.setCategoryComboBox.addItem(u'obvodem')
        self.setCategoryComboBox.setItemData(
            1, u'Zařadit všechny parcely do kategorií na základě obvodu',
            Qt.ToolTipRole)
        self.setCategoryComboBox.currentIndexChanged.connect(
            self._set_setCategoryValue)
        self.gridLayout.addWidget(self.setCategoryComboBox, 5, 1, 1, 1)
        
        self.setCategoryPushButton = QPushButton(self)
        self.setCategoryPushButton.setObjectName(u'setCategoryPushButton')
        self.setCategoryPushButton.setText(u'Zařadit')
        self.setCategoryPushButton.clicked.connect(
            self._start_setting_pu_category)
        self.gridLayout.addWidget(self.setCategoryPushButton, 5, 2, 1, 1)
    
    def _set_icon_size(self):
        """Sets editToolBar icon size according to the current QGIS settings."""
        
        self.editToolBar.setIconSize(self.iface.mainWindow().iconSize())
    
    
    def _set_categoryValue(self):
        """Sets categoryValue according to the current index.
        
        categoryValue - description:
            0 - mimo obvod
            1 - v obvodu - neřešené
            2 - v obvodu - řešené
        
        """
        
        currentIndex = self.categoryComboBox.currentIndex()
        
        if currentIndex == 3:
            self.categoryValue = None
        else:
            self.categoryValue = currentIndex
    
    def _set_setCategoryValue(self):
        """Sets setCategoryValue according to the current index.
        
        setCategoryValue - description:
            0 - vybrané parcely
            1 - obvodem
        
        """
        
        self.setCategoryValue = self.setCategoryComboBox.currentIndex()
    
    def set_perimeter_layer(self, perimeterLayer, lastPerimeterLayer=True):
        """Sets the perimeter layer in the perimeterMapLayerComboBox.
        
        Args:
            perimeterLayer (QgsVectorLayer): A reference to the perimeter layer.
            lastPerimeterLayer (bool): True to set self.lastPerimeterLayer,
                False otherwise.
        
        """
        
        if lastPerimeterLayer:
            self.lastPerimeterLayer = perimeterLayer
        
        self.perimeterMapLayerComboBox.setLayer(perimeterLayer)
    
    def sync_perimeter_map_layer_combo_box(self):
        """Synchronizes perimeter map layer combo boxes.
        
        Synchronizes with the perimeterMapLayerComboBox in the perimeterWidget.
        
        """
        
        perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
        
        if perimeterLayer != self.lastPerimeterLayer:
            self.lastPerimeterLayer = perimeterLayer
        
            self.dW.stackedWidget.checkAnalysisPuWidget\
                .perimeterPuCaWidget.set_perimeter_layer(perimeterLayer)
    
    def _reset_perimeter_layer(self):
        """Resets the perimeter layer."""
        
        layers = self.iface.legendInterface().layers()
        
        if self.lastPerimeterLayer not in layers:
            self.set_perimeter_layer(None)
    
    def _rollback_perimeter_layer(self):
        """Rolls the perimeter layer back."""
        
        if self.lastPerimeterLayer == None:
            self.set_perimeter_layer(self.lastPerimeterLayer, False)
        else:
            self.lastPerimeterLayer = \
                self.perimeterMapLayerComboBox.currentLayer()
    
    def _create_perimeter(self):
        """Calls methods for creating and loading perimeter layer."""
        
        try:
            succes, layer = self.dW.check_layer(self)
            
            if not succes:
                return
            
            if layer.featureCount() == 0:
                self.set_text_statusbar.emit(
                    u'Aktivní vrstva neobsahuje žádný prvek.', 10, True)
                return
            
            editing = self.dW.check_editing()
            
            title = u'Uložit vrstvu obvodu jako...'
            filters = u'.shp (*.shp)'
            
            perimeterLayerFilePath = self.dW.open_file_dialog(
                title, filters, False)
            
            if perimeterLayerFilePath:
                self.set_text_statusbar.emit(
                    u'Vytvářím vrstvu obvodu...', 0, False)
                
                fileInfo = QFileInfo(perimeterLayerFilePath)
                
                if not fileInfo.suffix() == u'shp':
                    perimeterLayerFilePath = \
                        fileInfo.absoluteFilePath() + u'.shp'
                    fileInfo = QFileInfo(perimeterLayerFilePath)
                
                selectedFeaturesIds = layer.selectedFeaturesIds()
                
                perimeterLayerName = fileInfo.completeBaseName()
                
                loadedLayer = self.dW.check_loaded_layers(
                    perimeterLayerFilePath)
                
                perimeterLayer = self._create_perimeter_layer(
                    layer, perimeterLayerFilePath, self.categoryName,
                    perimeterLayerName, loadedLayer)
                
                QgsApplication.processEvents()
                
                loadedLayer = self.dW.check_loaded_layers(
                    perimeterLayerFilePath)
                
                if loadedLayer:
                    self.iface.actionDraw().trigger()
                    self.set_perimeter_layer(loadedLayer, False)
                    self.sync_perimeter_map_layer_combo_box()
                else:
                    QgsMapLayerRegistry.instance().addMapLayer(perimeterLayer)
                
                layer.selectByIds(selectedFeaturesIds)
                
                self.iface.setActiveLayer(layer)
                
                if editing:
                    self.toggleEditingAction.trigger()
                
                self.set_text_statusbar.emit(
                    u'Obvod byl úspešně vytvořen.', 15, False)
        except:
            self.dW.display_error_messages(
                self,
                u'Error creating perimeter.',
                u'Chyba při vytváření obvodu.')
    
    def _create_perimeter_layer(
            self,
            layer, perimeterLayerFilePath, categoryName,
            perimeterLayerName, loadedLayer):
        """Creates a perimeter layer from the given layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayerFilePath (str): A full path to the perimeter layer.
            categoryName (str): A name of the category field the layer is about
                to be dissolved by.
            perimeterLayerName (str): A name of the perimeter layer.
            loadedLayer (bool): A reference to the loaded layer.
                This is relevant only for Windows platform.
        
        Returns:
            QgsVectorLayer: A reference to the perimeter layer.
        
        """
        
        fileInfo = QFileInfo(perimeterLayerFilePath)
        
        tempPerimeterLayerName = fileInfo.completeBaseName() + u'.temp'
        
        layer.removeSelection()
        
        tempPerimeterLayerPath = processing.runalg(
            'qgis:dissolve',
            layer, False, categoryName, None)['OUTPUT']
            
        tempPerimeterLayer = QgsVectorLayer(
            tempPerimeterLayerPath, tempPerimeterLayerName, 'ogr')
        
        if loadedLayer:
            perimeterLayerName = loadedLayer.name()
            QgsMapLayerRegistry.instance().removeMapLayer(loadedLayer)
        
        QgsApplication.processEvents()
        
        processing.runalg(
            'qgis:multiparttosingleparts',
            tempPerimeterLayer, perimeterLayerFilePath)
        
        perimeterLayer = QgsVectorLayer(
            perimeterLayerFilePath, perimeterLayerName, 'ogr')
        
        QgsMapLayerRegistry.instance().addMapLayer(perimeterLayer)
        
        expression = QgsExpression(
            "\"{}\" is null".format(self.shortCategoryName))
        
        self.dW.delete_features_by_expression(perimeterLayer, expression)
        
        return perimeterLayer
    
    def set_perimeter_layer_table_config(self, perimeterLayer):
        """Sets perimeter layer table config.
        
        Args:
            layer (QgsVectorLayer): A reference to the perimeter layer.
        
        """
        
        fields = perimeterLayer.pendingFields()
        
        tableConfig = perimeterLayer.attributeTableConfig()
        tableConfig.update(fields)
        
        columns = tableConfig.columns()
        
        for column in columns:
            if not column.name == self.shortCategoryName:
                column.hidden = True
        
        tableConfig.setColumns(columns)
        perimeterLayer.setAttributeTableConfig(tableConfig)
    
    def _start_setting_pu_category(self):
        """Starts setting PU category in a separate thread.."""
        
        succes, layer = self.dW.check_layer(self)
        
        if not succes:
            return
        
        self.executeThread = ExecuteThread(layer)
        self.executeThread.started.connect(self._run_setting_pu_category)
        self.executeThread.start()
    
    def _run_setting_pu_category(self, layer):
        """Calls methods for setting PU category.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        """
        try:
            perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
            
            editing = self.dW.check_editing()
            
            if self.setCategoryValue == 0:
                self._set_category_for_selected(layer, perimeterLayer)
            
            if self.setCategoryValue == 1:
                self._set_category_by_perimeter(layer, perimeterLayer)
            
            if editing:
                self.toggleEditingAction.trigger()
        except:
            QgsApplication.processEvents()
            
            self.dW.display_error_messages(
                self,
                u'Error setting parcel category.',
                u'Chyba při zařazování do kategorie parcel.')
    
    def _set_category_for_selected(self, layer, perimeterLayer):
        """Sets a categoryValue to categoryName column for selected features.
        
        Also updates the perimeter layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
        featureCount = layer.selectedFeatureCount()
        
        if featureCount == 0:
            self.set_text_statusbar.emit(
                u'V aktivní vrstvě nejsou vybrány žádné prvky.', 10, True)
            return
        
        currentCategory = self.categoryComboBox.currentText()
        
        warning = False
        
        if featureCount == 1:
            self.set_text_statusbar.emit(
                u'Zařazuji vybranou parcelu do kategorie "{}"...'
                .format(currentCategory), 0, warning)
        else:
            self.set_text_statusbar.emit(
                u'Zařazuji vybrané parcely do kategorie "{}"...'
                .format(currentCategory), 0, warning)
        
        selectedFeaturesIds = layer.selectedFeaturesIds()
        selectedFeatures = layer.selectedFeaturesIterator()
        
        self.dW.set_field_value_for_features(
            layer, selectedFeatures, self.categoryName, self.categoryValue)
        
        QgsApplication.processEvents()
        
        self.update_perimeter_layer(layer, perimeterLayer)
        
        layer.selectByIds(selectedFeaturesIds)
        
        if featureCount == 1:
            self.set_text_statusbar.emit(
                u'Vybraná parcela byla zařazena do kategorie "{}".'
                .format(currentCategory), 20, warning)
        else:
            self.set_text_statusbar.emit(
                u'Vybrané parcely byly zařazeny do kategorie "{}".'
                .format(currentCategory), 20, warning)
    
    def update_perimeter_layer(self, layer=None, perimeterLayer=None):
        """Updates the perimeter layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
        if not layer:
            layer = self.iface.activeLayer()
        
        if not perimeterLayer:
            perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
        
        if not self.dW.check_perimeter_layer(perimeterLayer, layer):
            # SpatiaLite fix - start
            perimeterString = u'-obvod.shp'
            
            if not self.dW.fixedSqliteDriver:
                composedURI = QgsDataSourceURI(layer.source())
                perimeterLayerFilePath = \
                    composedURI.database().split('.sdb')[0] + perimeterString
            else:
                perimeterLayerFilePath = \
                    layer.source().split('.db')[0] + perimeterString
            # SpatiaLite fix - end
            
            fileInfo = QFileInfo(perimeterLayerFilePath)
            perimeterLayerName = fileInfo.baseName()
            
            loadedLayer = self.dW.check_loaded_layers(perimeterLayerFilePath)
            
            perimeterLayer = self._create_perimeter_layer(
                layer, perimeterLayerFilePath, self.categoryName,
                perimeterLayerName, loadedLayer)
            
            QgsApplication.processEvents()
            
            loadedLayer = self.dW.check_loaded_layers(perimeterLayerFilePath)
            
            if loadedLayer:
                self.iface.actionDraw().trigger()
                self.set_perimeter_layer(loadedLayer, False)
                self.sync_perimeter_map_layer_combo_box()
            else:
                QgsMapLayerRegistry.instance().addMapLayer(perimeterLayer)
        else:
            perimeterLayerFilePath = perimeterLayer.source()
            perimeterLayerName = perimeterLayer.name()
            
            perimeterLayer = self._create_perimeter_layer(
                layer, perimeterLayerFilePath, self.categoryName,
                perimeterLayerName, perimeterLayer)
            
            self.set_perimeter_layer(perimeterLayer, False)
            self.sync_perimeter_map_layer_combo_box()
        
        QgsApplication.processEvents()
        
        self.iface.actionDraw().trigger()
    
        self.iface.setActiveLayer(layer)
    
    def _set_category_by_perimeter(self, layer, perimeterLayer):
        """Sets a categoryValue to categoryName column for all features
        according to current layer in perimeterMapLayerComboBox.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            perimeterLayer (QgsVectorLayer): A reference to the perimeter
                layer.
        
        """
        
        if not self.dW.check_perimeter_layer(perimeterLayer, layer, self):
            return
        
        if perimeterLayer.featureCount() == 0:
            self.set_text_statusbar.emit(
                u'Vrstva obvodu neobsahuje žádný prvek.', 10, True)
            return
        
        warning = False
        
        self.set_text_statusbar.emit(
            u'Zařazuji parcely do kategorií na základě obvodu...', 0, warning)
        
        selectedFeaturesIds = layer.selectedFeaturesIds()
        perimeterSelectedFeaturesIds = perimeterLayer.selectedFeaturesIds()
        
        layer.removeSelection()
        perimeterLayer.removeSelection()
        
        for categoryValue in self.categoryValues:
            if categoryValue == None:
                perimeterLayer.selectAll()
            else:
                self.dW.select_features_by_field_value(
                    perimeterLayer, self.shortCategoryName, categoryValue)
            
            if perimeterLayer.selectedFeatureCount() != 0:
                selectedFeaturesLayerFilePath = processing.runalg(
                    'qgis:saveselectedfeatures',
                    perimeterLayer, None)['OUTPUT_LAYER']
                
                selectedFeaturesLayer = QgsVectorLayer(
                    selectedFeaturesLayerFilePath,
                    'selectedFeaturesLayer', 'ogr')
                
                processing.runalg(
                    'qgis:selectbylocation',
                    layer, selectedFeaturesLayer, u'within', 0, 0)
                
                if categoryValue == None:
                    layer.invertSelection()
                    categoryValue = QPyNullVariant
                
                features = layer.selectedFeaturesIterator()
                
                self.dW.set_field_value_for_features(
                    layer, features, self.categoryName, categoryValue)
        
        layer.selectByIds(selectedFeaturesIds)
        perimeterLayer.selectByIds(perimeterSelectedFeaturesIds)
        
        self.set_text_statusbar.emit(
            u'Zařazení parcel na základě obvodu úspěšně dokončeno.',
            30, warning)
        
    def _select_category(self):
        """Selects features in the current category."""
        
        try:
            succes, layer = self.dW.check_layer(self)
            
            if not succes:
                return
            
            if self.categoryValue == None:
                expression = QgsExpression(
                    "\"{}\" is null".format(self.categoryName))
                self.dW.select_features_by_expression(layer, expression)
            else:
                self.dW.select_features_by_field_value(
                    layer, self.categoryName, self.categoryValue)
            
            currentCategory = self.categoryComboBox.currentText()
            
            featureCount = layer.selectedFeatureCount()
            
            duration = 10
            warning = False
            
            if featureCount == 0:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" není žádná parcela.'
                    .format(currentCategory), duration, warning)
            elif featureCount == 1:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" je {} parcela.'
                    .format(currentCategory, featureCount), duration, warning)
            elif 1 < featureCount < 5:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" jsou {} parcely.'
                    .format(currentCategory, featureCount), duration, warning)
            elif 5 <= featureCount:
                self.set_text_statusbar.emit(
                    u'V kategorii "{}" je {} parcel.'
                    .format(currentCategory, featureCount), duration, warning)
        except:
            self.dW.display_error_messages(
                self,
                u'Error selecting parcels in category.',
                u'Chyba při vybírání parcel v kategorii.')
    
    def check_perimeter_map_layer_combo_box(self):
        """Checks if there is a layer in perimeterMapLayerComboBox.
        
        Returns:
            bool: True when there is a layer in perimeterMapLayerComboBox,
                False otherwise.
        
        """
        
        if self.perimeterMapLayerComboBox.currentLayer():
            return True
        else:
            return False

