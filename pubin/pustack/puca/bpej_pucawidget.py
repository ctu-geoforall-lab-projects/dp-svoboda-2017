# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BpejPuCaWidget and BpejLabelPuCaWidget
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

from PyQt4.QtGui import QWidget, QVBoxLayout, QLabel, QComboBox
from PyQt4.QtCore import Qt, QDir, QFileInfo

from qgis.gui import (QgsMapLayerComboBox, QgsMapLayerProxyModel,
                      QgsFieldComboBox, QgsMessageBar)
from qgis.core import *

import processing

from collections import defaultdict
from datetime import datetime

import os
import urllib
import zipfile
import csv

from pucawidget import PuCaWidget


class BpejPuCaWidget(PuCaWidget):
    """A widget for 'BPEJ' analysis."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.lastBpejLayer = None
        
        self.bpejMapLayerComboBox = QgsMapLayerComboBox(self)
        self.bpejMapLayerComboBox.setObjectName(u'bpejMapLayerComboBox')
        self.bpejMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._rollback_bpej_layer)
        QgsMapLayerRegistry.instance().layersRemoved.connect(
            self._reset_bpej_layer)
        self.set_bpej_layer(self.lastBpejLayer)
        self.vBoxLayout.addWidget(self.bpejMapLayerComboBox)
        
        self.bpejFieldComboBox = QgsFieldComboBox(self)
        self.bpejFieldComboBox.setObjectName(u'bpejFieldComboBox')
        self.bpejFieldComboBox.setLayer(
            self.bpejMapLayerComboBox.currentLayer())
        self.vBoxLayout.addWidget(self.bpejFieldComboBox)
        
        self.bpejMapLayerComboBox.layerChanged.connect(
            self.bpejFieldComboBox.setLayer)
    
    def set_bpej_layer(self, bpejLayer, lastBpejLayer=True):
        """Sets the BPEJ layer in the bpejMapLayerComboBox.
        
        Args:
            bpejLayer (QgsVectorLayer): A reference to the BPEJ layer.
            lastBpejLayer (bool): True to set self.lastBpejLayer,
                False otherwise.
        
        """
        
        if lastBpejLayer:
            self.lastBpejLayer = bpejLayer
        
        self.bpejMapLayerComboBox.setLayer(bpejLayer)
    
    def _reset_bpej_layer(self):
        """Resets the BPEJ layer."""
        
        layers = self.iface.legendInterface().layers()
        
        if self.lastBpejLayer not in layers:
            self.set_bpej_layer(None)
    
    def _rollback_bpej_layer(self):
        """Rollbacks the BPEJ layer."""
        
        if self.lastBpejLayer == None:
            self.set_bpej_layer(self.lastBpejLayer, False)
        else:
            self.lastBpejLayer = self.bpejMapLayerComboBox.currentLayer()
    
    def execute(self, layer):
        """Executes the analysis.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
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
            
            layer.removeSelection()
            bpejLayer.removeSelection()
            
            bpejField = self._edit_bpej_field(bpejField, layer)
            
            unionOutput = processing.runalg(
                'qgis:union', layer, bpejLayer, None)['OUTPUT']
            
            unionLayer = QgsVectorLayer(unionOutput, 'unionLayer', 'ogr')
            
            expression = QgsExpression(
                "\"{}\" is null "
                "or "
                "\"{}\" is null"\
                .format(
                    bpejField,
                    self.dW.visibleDefaultColumnsPAR[0][:10]))
            
            self.dW.delete_features_by_expression(unionLayer, expression)
            
            multiToSingleOutput = processing.runalg(
                'qgis:multiparttosingleparts', unionLayer, None)['OUTPUT']
            
            multiToSingleLayer = QgsVectorLayer(
                multiToSingleOutput, 'multiToSingleLayer', 'ogr')
            
            bpejCodePrices = self._get_bpej_code_prices()
            
            puIDColumnName = 'rowid'
            
            featurePrices, missingBpejCodes = self._calculate_feature_prices(
                puIDColumnName, multiToSingleLayer, bpejField, bpejCodePrices)
            
            priceFieldName = self.dW.requiredColumnsPAR[4]
            
            priceFieldID = layer.fieldNameIndex(priceFieldName)
            
            layer.startEditing()
            layer.updateFields()
            
            features = layer.getFeatures()
            
            for feature in features:
                featurePuID = feature.attribute(puIDColumnName)
                featureID = feature.id()
                featurePrice = feature.attribute(priceFieldName)
                
                price = featurePrices[featurePuID]
                roundedPrice = round(price, -1)
                
                if roundedPrice != featurePrice:
                    layer.changeAttributeValue(
                        featureID, priceFieldID, roundedPrice)
            
            layer.commitChanges()
            
            if editing:
                self.iface.actionToggleEditing()
            
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
        except self.dW.puError:
            QgsApplication.processEvents()
        except:
            QgsApplication.processEvents()
            
            currentCheckAnalysisName = \
                self.pW.checkAnalysisComboBox.currentText()
            
            self.dW.display_error_messages(
                u'Error executing "{}".'.format(currentCheckAnalysisName),
                u'Chyba při provádění "{}".'.format(currentCheckAnalysisName))
    
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
    
    def _get_bpej_code_prices(self):
        """Gets BPEJ code prices."""
        
        formatTimeStr = '%d.%m.%Y'
        
        bpejDir = QDir(self.dW.pluginDir + u'/data/bpej')
        
        bpejBaseName = u'SC_BPEJ'
        
        bpejZipFileName = bpejBaseName + u'.zip'
        
        bpejZipFilePath = bpejDir.filePath(bpejZipFileName)
        
        bpejCsvFileName = bpejBaseName + u'.csv'
        
        bpejCsvFilePath = bpejDir.filePath(bpejCsvFileName)
        
        upToDate = self._check_bpej_csv(bpejCsvFilePath, formatTimeStr)
        
        if not upToDate:
            googleUrl = 'https://www.google.com'
            
            bpejZipUrl = 'http://www.cuzk.cz/CUZK/media/CiselnikyISKN/' + \
                'SC_BPEJ/SC_BPEJ.zip?ext=.zip'
            
            self._download_bpej_csv(
                googleUrl, bpejZipUrl, bpejZipFilePath, bpejCsvFileName)
        
        bpejCodePrices = self._read_bpej_csv(bpejCsvFilePath, formatTimeStr)
        
        return bpejCodePrices
    
    def _check_bpej_csv(self, bpejCsvFilePath, formatTimeStr):
        """Checks if the BPEJ CSV file is up-to-date.
        
        Args:
            bpejCsvFilePath (str): A full path to the BPEJ CSV file.
            formatTimeStr (str): A string for time formatting.
        
        Returns:
            bool: True when the BPEJ CSV file is up-to-date, False otherwise.
        
        """
        
        modificationEpochTime = os.path.getmtime(bpejCsvFilePath)
        
        modificationDateTime = datetime.fromtimestamp(modificationEpochTime)
        
        todayDateTime = datetime.now()
        
        bpejTodayDateTime = todayDateTime.replace(
            hour=03, minute=06, second=0, microsecond=0)
        
        if modificationDateTime > bpejTodayDateTime:
            return True
        else:
            return False
    
    def _download_bpej_csv(
            self, googleUrl, bpejZipUrl, bpejZipFilePath, bpejCsvFileName):
        """Downloads BPEJ CSV file and unzips it.
        
        Args:
            googleUrl (str): A Google URL.
            bpejZipUrl (str): An URL of BPEJ ZIP file.
            bpejZipFilePath (str): A full path to the BPEJ ZIP file.
            bpejCsvFileName (str): A name of the BPEJ CSV file.
        
        Raises:
            dw.puError: When a connection to the CUZK failed.
        
        """
        
        try:
            testGoogleConnection = urllib.urlopen(googleUrl)
        except:
            return
        else:
            testGoogleConnection.close()
        
        try:
            testBpejConnection = urllib.urlopen(bpejZipUrl)
        except:
            raise self.dW.puError(
                self.dW,
                u'A Connection to "{}" failed.'.format(bpejZipUrl),
                u'Nepodařilo se připojit k "{}"'.format(bpejZipUrl))
        else:
            testBpejConnection.close()
            
            urllib.urlretrieve(bpejZipUrl, bpejZipFilePath)
            
            self._unzip_bpej_zip(bpejZipFilePath, bpejCsvFileName)
            
            os.remove(bpejZipFilePath)
    
    def _unzip_bpej_zip(self, bpejZipFilePath, bpejCsvFileName):
        """Unzips BPEJ ZIP file into the same directory.
        
        Args:
            bpejZipFilePath (str): A full path to the BPEJ ZIP file.
            bpejCsvFileName (str): A name of the BPEJ CSV file.
        
        """
        
        fileInfo = QFileInfo(bpejZipFilePath)
        
        bpejDir = fileInfo.absolutePath()
        
        bpejZip = zipfile.ZipFile(bpejZipFilePath, 'r')
        
        bpejZipContent = bpejZip.namelist()
        
        if len(bpejZipContent) != 1:
            bpejZip.close()
            
            raise self.dW.puError(
                self.dW,
                u'The structure of the BPEJ ZIP file has changed. '
                u'The BPEJ ZIP file contains more than one file.',
                u'Struktura stahovaného BPEJ ZIP souboru se změnila.')
        
        bpejZipFirstMember = bpejZipContent[0]
        
        bpejZip.extract(bpejZipFirstMember, bpejDir)
        bpejZip.close()
        
        if bpejZipFirstMember != bpejCsvFileName:
            bpejDir = QDir(bpejDir)
            
            bpejZipFirstMemberFilePath = bpejDir.filePath(bpejZipFirstMember)
            
            bpejCsvFilePath = bpejDir.filePath(bpejCsvFileName)
            
            os.rename(bpejZipFirstMemberFilePath, bpejCsvFilePath)
    
    def _read_bpej_csv(self, bpejCsvFilePath, formatTimeStr):
        """Reads the BPEJ CSV file.
        
        Args:
            bpejCsvFilePath (str): A full path to the BPEJ CSV file.
            formatTimeStr (str): A string for time formatting.
        
        Returns:
            dict: A dictionary with BPEJ codes as keys (str)
                and prices as values (flt).
        
        """
               
        with open(bpejCsvFilePath, 'rb') as bpejCsvFile:
            bpejCsvReader = csv.reader(bpejCsvFile, delimiter=';')
            
            columnNames = bpejCsvReader.next()
            
            codeColumnIndex = columnNames.index('KOD')
            priceColumnIndex = columnNames.index('CENA')
            validFromColumnIndex = columnNames.index('PLATNOST_OD')
            validToColumnIndex = columnNames.index('PLATNOST_DO')
            
            todayDate = datetime.now().date()
            
            bpejCodePrices = {}
            
            for row in bpejCsvReader:
                if len(row) == 0:
                    break
                
                validFromDateStr = row[validFromColumnIndex]
                validFromDate = datetime.strptime(
                    validFromDateStr, formatTimeStr).date()
                
                validToDateStr = row[validToColumnIndex]
                
                if validToDateStr == '':
                    validToDate = todayDate
                else:
                    validToDate = datetime.strptime(
                        validToDateStr, formatTimeStr).date()
                
                if validFromDate <= todayDate <= validToDate:
                    code = row[codeColumnIndex]
                    price = row[priceColumnIndex]
                    
                    bpejCodePrices[code] = float(price)
        
        return bpejCodePrices
    
    def _calculate_feature_prices(
            self,
            puIDColumnName, multiToSingleLayer, bpejField, bpejCodePrices):
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


class BpejLabelPuCaWidget(PuCaWidget):
    """A label widget for 'BPEJ' analysis."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.bpejLayerLabel = QLabel(self)
        self.bpejLayerLabel.setObjectName(u'bpejLayerLabel')
        self.bpejLayerLabel.setText(u'BPEJ:')
        self.bpejLayerLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.bpejLayerLabel)
        
        self.bpejPriceLabel = QLabel(self)
        self.bpejPriceLabel.setObjectName(u'bpejPriceLabel')
        self.bpejPriceLabel.setText(u'Sloupec kódu BPEJ:')
        self.bpejPriceLabel.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.bpejPriceLabel)

