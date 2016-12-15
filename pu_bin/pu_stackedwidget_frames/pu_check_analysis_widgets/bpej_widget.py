# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BpejWidget
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

from PyQt4.QtGui import QWidget, QGridLayout, QLabel
from PyQt4.QtCore import QPyNullVariant, Qt

from qgis.gui import (QgsMapLayerComboBox, QgsMapLayerProxyModel,
                      QgsFieldComboBox, QgsFieldProxyModel)
from qgis.core import *

import processing

from collections import defaultdict


class BpejWidget(QWidget):
    """A widget for 'BPEJ' analysis."""
    
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
        
        super(BpejWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'bpejWidget')
        
        self.bpejGridLayout = QGridLayout(self)
        self.bpejGridLayout.setObjectName(u'bpejGridLayout')
        self.bpejGridLayout.setAlignment(Qt.AlignTop)
        self.bpejGridLayout.setContentsMargins(0, 0, 0, 0)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.bpejLayerLabel = QLabel(self)
        self.bpejLayerLabel.setObjectName(u'bpejLayerLabel')
        self.bpejLayerLabel.setText(u'Vrstva BPEJ:')
        self.bpejGridLayout.addWidget(self.bpejLayerLabel, 0, 0, 1, 1)
        
        self.bpejMapLayerComboBox = QgsMapLayerComboBox(self)
        self.bpejMapLayerComboBox.setObjectName(u'bpejMapLayerComboBox')
        self.bpejMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.bpejGridLayout.addWidget(self.bpejMapLayerComboBox, 0, 1, 1, 1)
        
        self.bpejGridLayout.setColumnStretch(1, 1)
        
        self.bpejPriceLabel = QLabel(self)
        self.bpejPriceLabel.setObjectName(u'bpejPriceLabel')
        self.bpejPriceLabel.setText(u'Sloupec ceny [Kč/m]:')
        self.bpejGridLayout.addWidget(self.bpejPriceLabel, 1, 0, 1, 1)
        
        self.bpejFieldComboBox = QgsFieldComboBox(self)
        self.bpejFieldComboBox.setObjectName(u'bpejFieldComboBox')    
        self.bpejFieldComboBox.setFilters(QgsFieldProxyModel.Numeric)
        self.bpejFieldComboBox.setLayer(
            self.bpejMapLayerComboBox.currentLayer())
        self.bpejGridLayout.addWidget(self.bpejFieldComboBox, 1, 1, 1, 1)
        
        self.bpejMapLayerComboBox.layerChanged.connect(
            self.bpejFieldComboBox.setLayer)
    
    def execute(self, layer):
        """Executes the analysis.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            editing = self.dW.stackedWidget.check_editing()
            
            bpejField = self.bpejFieldComboBox.currentField()
            
            if bpejField == u'':
                self.pW.text_statusbar.emit(
                    u'Není vybrán sloupec ceny.', 7000)
                return
            
            bpejField = bpejField[:10]
            
            parFields = layer.pendingFields()
            
            for field in parFields:
                if bpejField.lower() == field.name().lower():
                    if len(bpejField) <= 8:
                        bpejField = bpejField + '_2'
                        break
                    elif len(bpejField) == 9:
                        bpejField = bpejField + '_'
                        break
                    elif len(bpejField) == 10:
                        bpejField = bpejField[:8]
                        bpejField = bpejField + '_1'
                        break
            
            bpejLayer = self.bpejMapLayerComboBox.currentLayer()
            
            bpejLayerCrs = bpejLayer.crs().authid()
            layerCrs = layer.crs().authid()
            
            if bpejLayerCrs != layerCrs:
                self.pW.text_statusbar.emit(
                    u'Aktivní vrstva a vrstva BPEJ nemají stejný '
                    u'souřadnicový systém.', 7000)
                return
            
            self.pW.text_statusbar.emit(
                u'Provádím analýzu - oceňování podle BPEJ.', 0)
            
            unionOutput = processing.runalg(
                'qgis:union', layer, bpejLayer, None)['OUTPUT']
            
            unionLayer = QgsVectorLayer(unionOutput, 'unionLayer', 'ogr')
            
            expression = QgsExpression(
                "\"{}\" is null "
                "or "
                "(\"KMENOVE_CI\" is null and \"PU_KATEGOR\" is null)"\
                .format(bpejField))
            
            featuresToDelete = unionLayer.getFeatures(
                QgsFeatureRequest(expression))
            
            featuresToDeleteID = [feature.id() for feature in featuresToDelete]
            
            unionLayer.startEditing()
            unionLayer.updateFields()
            
            unionLayer.deleteFeatures(featuresToDeleteID)
            
            unionLayer.commitChanges()
            
            multiToSingleOutput = processing.runalg(
                'qgis:multiparttosingleparts', unionLayer, None)['OUTPUT']
            
            multiToSingleLayer = QgsVectorLayer(
                multiToSingleOutput, 'multiToSingleLayer', 'ogr')
            
            puIDColumnName = 'rowid'
            
            featurePrices = defaultdict(float)
            
            features = multiToSingleLayer.getFeatures()
            
            for feature in features:
                featurePuID = long(feature.attribute(puIDColumnName))
                featureBpejPrice = feature.attribute(bpejField)
                featureGeometry = feature.geometry()
                
                if featureGeometry != None:
                    featureArea = featureGeometry.area()
                    
                    price = featureBpejPrice*featureArea
                    
                    featurePrices[featurePuID] += price
            
            fieldID = layer.fieldNameIndex('PU_CENA')
            
            layer.startEditing()
            layer.updateFields()
            
            features = layer.getFeatures()
            
            for feature in features:
                featurePuID = feature.attribute(puIDColumnName)
                featureID = feature.id()
                
                price = featurePrices[featurePuID]
                roundedPrice = round(price, -1)
                
                if roundedPrice != 0:
                    layer.changeAttributeValue(featureID, fieldID, roundedPrice)
            
            layer.commitChanges()
            
            if editing == True:
                self.dW.stackedWidget.editFrame.toggleEditingAction.trigger()
            
            self.pW.text_statusbar.emit(
                u'Analýza oceňování podle BPEJ úspěšně dokončena.', 15000)
        except:
            currentAnalysisName = self.pW.checkAnalysisComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing "{}".'.format(currentAnalysisName),
                u'Chyba při provádění "{}".'.format(currentAnalysisName))

