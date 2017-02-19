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
from PyQt4.QtCore import QPyNullVariant, Qt, QDir

from qgis.gui import (QgsMapLayerComboBox, QgsMapLayerProxyModel,
                      QgsFieldComboBox, QgsFieldProxyModel, QgsMessageBar)
from qgis.core import *

import processing

from collections import defaultdict
import csv
import time


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
        self.lastBpejLayer = None
        
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
        self.bpejMapLayerComboBox.setLayer(self.lastBpejLayer)
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._set_bpej_layer)
        
        self.bpejGridLayout.setColumnStretch(1, 1)
        
        self.bpejPriceLabel = QLabel(self)
        self.bpejPriceLabel.setObjectName(u'bpejPriceLabel')
        self.bpejPriceLabel.setText(u'Sloupec kódu BPEJ:')
        self.bpejGridLayout.addWidget(self.bpejPriceLabel, 1, 0, 1, 1)
        
        self.bpejFieldComboBox = QgsFieldComboBox(self)
        self.bpejFieldComboBox.setObjectName(u'bpejFieldComboBox')    
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
        
        editing = self.dW.check_editing()
        
        bpejField = self.bpejFieldComboBox.currentField()
        
        if bpejField == u'':
            self.pW.set_text_statusbar.emit(
                u'Není vybrán sloupec ceny.', 10)
            return
        
        bpejLayer = self.bpejMapLayerComboBox.currentLayer()
        
        bpejLayerCrs = bpejLayer.crs().authid()
        layerCrs = layer.crs().authid()
        
        if bpejLayerCrs != layerCrs:
            self.pW.set_text_statusbar.emit(
                u'Aktivní vrstva a vrstva BPEJ nemají stejný '
                u'souřadnicový systém.', 10)
            return
        
        self.pW.set_text_statusbar.emit(
            u'Provádím analýzu - oceňování podle BPEJ...', 0)
        
        bpejField = self._edit_bpej_field(bpejField, layer)
        
        unionOutput = processing.runalg(
            'qgis:union', layer, bpejLayer, None)['OUTPUT']
        
        unionLayer = QgsVectorLayer(unionOutput, 'unionLayer', 'ogr')
        
        expression = QgsExpression(
            "\"{}\" is null "
            "or "
            "(\"{}\" is null and \"{}\" is null)"\
            .format(
                bpejField,
                self.dW.visibleDefaultColumnsPAR[0][:10],
                self.dW.allPuColumnsPAR[3][:10]))
        
        self.dW.delete_features_by_expression(unionLayer, expression)
        
        multiToSingleOutput = processing.runalg(
            'qgis:multiparttosingleparts', unionLayer, None)['OUTPUT']
        
        multiToSingleLayer = QgsVectorLayer(
            multiToSingleOutput, 'multiToSingleLayer', 'ogr')
        
        bpejCodePrices = self._read_bpej_csv()
        
        puIDColumnName = 'rowid'
        
        featurePrices, missingBpejCodes = self._calculate_feature_prices(
            puIDColumnName, multiToSingleLayer, bpejField, bpejCodePrices)
        
        fieldID = layer.fieldNameIndex(self.dW.visiblePuColumnsPAR[4])
        
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
        
        if editing:
            self.dW.stackedWidget.editFrame.toggleEditingAction.trigger()
        
        if len(missingBpejCodes) != 0:
            missingBpejCodesStr = ', '.join(missingBpejCodes)
            
            expression = QgsExpression(
                "\"{}\" in ({})".format(bpejField, missingBpejCodesStr))
            
            self.dW.select_features_by_expression(bpejLayer, expression)
            
            self.iface.messageBar().pushMessage(
                u'BPEJ kód vybraných prvků ve vrstvě BPEJ nebyl nalezen.',
                QgsMessageBar.WARNING, 15)
        
        self.pW.set_text_statusbar.emit(
            u'Analýza oceňování podle BPEJ úspěšně dokončena.', 20)
    
    def _edit_bpej_field(self, bpejField, layer):
        """Edits BPEJ field name according to the layer fields.
        
        Args:
            bpejField (str): A name of the BPEJ field.
            layer (QgsVectorLayer): A reference to the active layer.
        
        Returns:
            str: An edited BPEJ field name
        
        """
        
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
                    bpejField = bpejField[:8] + '_1'
                    break
        
        return bpejField
    
    def _read_bpej_csv(self):
        """Reads the BPEJ CSV file.
        
        Returns:
            dict: A dictionary with BPEJ codes as keys (str)
                and prices as values (flt).
        
        """
        
        bpejCsvFilePath = self.dW.pluginDir + QDir.separator() + \
            u'data' + QDir.separator() + u'bpej' + QDir.separator() + \
            u'SC_BPEJ.csv'
        
        with open(bpejCsvFilePath, 'rb') as bpejCsvFile:
            bpejCsvReader = csv.reader(bpejCsvFile, delimiter=';')
            
            columnNames = bpejCsvReader.next()
            
            codeColumnIndex = columnNames.index('KOD')
            priceColumnIndex = columnNames.index('CENA')
            validFromColumnIndex = columnNames.index('PLATNOST_OD')
            validToColumnIndex = columnNames.index('PLATNOST_DO')
            
            formatStr = '%d.%m.%Y'
            
            todayDate = time.strptime(time.strftime(formatStr), formatStr)
            
            bpejCodePrices = {}
            
            for row in bpejCsvReader:
                if len(row) == 0:
                    break
                
                validFromDateStr = row[validFromColumnIndex]
                validFromDate = time.strptime(validFromDateStr, formatStr)
                
                validToDateStr = row[validToColumnIndex]
                
                if validToDateStr == '':
                    validToDate = todayDate
                else:
                    validToDate = time.strptime(validToDateStr, formatStr)
                
                if validFromDate <= todayDate <= validToDate:
                    code = row[codeColumnIndex]
                    price = row[priceColumnIndex]
                    
                    bpejCodePrices[code] = float(price)
        
        return bpejCodePrices
    
    def _calculate_feature_prices(self, puIDColumnName, multiToSingleLayer, bpejField, bpejCodePrices):
        """Calculates feature prices.
        
        Args:
            puIDColumnName (str): A name of PU ID column.
            multiToSingleLayer (QgsVectorLayer): A reference to the single
                features layer.
            bpejField (str): A name of the BPEJ field.
            bpejCodePrices (dict): A dictionary with BPEJ codes as keys (str)
                and prices as values (flt).
        
        Returns:
            defaultdict: A defaultdict with feature PU IDs as keys (long)
                and prices as values (float).
            set: A set of BPEJ codes that are not in BPEJ SCV file.
        
        """
        
        featurePrices = defaultdict(float)
        
        missingBpejCodes = set()
        
        features = multiToSingleLayer.getFeatures()
        
        for feature in features:
            featurePuID = long(feature.attribute(puIDColumnName))
            featureBpejCode = str(feature.attribute(bpejField))
            featureGeometry = feature.geometry()
            
            if featureGeometry != None:
                featureArea = featureGeometry.area()
                
                editedFeatureBpejCode = featureBpejCode.replace('.', '')
                
                if editedFeatureBpejCode in bpejCodePrices:
                    featureBpejPrice = bpejCodePrices[editedFeatureBpejCode]
                else:
                    featureBpejPrice = 0.0
                    missingBpejCodes.add(featureBpejCode)
                
                price = featureBpejPrice*featureArea
                
                featurePrices[featurePuID] += price
        
        return featurePrices, missingBpejCodes
    
    def _set_bpej_layer(self):
        """Sets current bpej layer.
        
        Sets current bpej layer to None if the last bpej layer was None.
        
        """
        
        if self.lastBpejLayer == None:
            self.bpejMapLayerComboBox.setLayer(self.lastBpejLayer)
        else:
            self.lastBpejLayer = self.bpejMapLayerComboBox.currentLayer()

