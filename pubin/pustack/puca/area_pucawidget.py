# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AreaPuCaWidget and AreaLabelPuCaWidget
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

from PyQt4.QtGui import QLabel, QLineEdit, QDoubleValidator
from PyQt4.QtCore import QPyNullVariant, Qt

from qgis.core import *

import processing

from collections import defaultdict
from math import sqrt

from pucawidget import PuCaWidget


class AreaPuCaWidget(PuCaWidget):
    """A widget for 'area' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            editing = self.dW.check_editing()
            
            self.pW.set_text_statusbar.emit(
                u'Provádím kontrolu - výměra nad mezní odchylkou...', 0)
            
            expression = QgsExpression("$geometry is not null")
            
            self.dW.select_features_by_expression(layer, expression)
            
            rowidColumnName = self.dW.rowidColumnName
            
            puAreaMaxQualityCodes = self._get_pu_area_max_quality_codes(
                layer, rowidColumnName)
            
            puAreaColumnName = self.dW.puAreaColumnName
            puAreaAbsDifferenceColumnName = \
                self.dW.puAreaAbsDifferenceColumnName
            puAreaLimitDeviationColumnName = \
                self.dW.puAreaLimitDeviationColumnName
            puAreaMaxQualityCodeColumnName = \
                self.dW.puAreaMaxQualityCodeColumnName
            
            puAreaFieldId = layer.fieldNameIndex(puAreaColumnName)
            puAreaAbsDifferenceFieldId = layer.fieldNameIndex(
                puAreaAbsDifferenceColumnName)
            puAreaLimitDeviationFieldId = layer.fieldNameIndex(
                puAreaLimitDeviationColumnName)
            puAreaMaxQualityCodeFieldId = layer.fieldNameIndex(
                puAreaMaxQualityCodeColumnName)
            
            layer.startEditing()
            layer.updateFields()
            
            exceededPuAreaLimitDeviationParIds = []
            
            features = layer.selectedFeaturesIterator()
            
            for feature in features:
                geometry = feature.geometry()
                
                originalPuArea = feature.attribute(puAreaColumnName)
                
                puArea = int(round(geometry.area()))
                defaultArea = feature.attribute(self.dW.deafultAreaColumnName)
                
                id = feature.id()
                
                if puArea != originalPuArea:
                    layer.changeAttributeValue(id, puAreaFieldId, puArea)
                
                if type(defaultArea) == QPyNullVariant:
                    continue
                
                originalPuAreaAbsDifference = feature.attribute(
                    puAreaAbsDifferenceColumnName)
                
                puAreaAbsDifference = abs(puArea-defaultArea)
                
                if puAreaAbsDifference != originalPuAreaAbsDifference:
                    layer.changeAttributeValue(
                        id, puAreaAbsDifferenceFieldId, puAreaAbsDifference)
                
                rowid = feature.attribute(rowidColumnName)
                puAreaMaxQualityCode = puAreaMaxQualityCodes[rowid]
                
                puAreaLimitDeviation = self._get_pu_area_limit_deviation(
                    puArea, defaultArea, puAreaMaxQualityCode)
                
                if puAreaLimitDeviation:
                    originalPuAreaLimitDeviation = feature.attribute(
                        puAreaLimitDeviationColumnName)
                    
                    if puAreaLimitDeviation != originalPuAreaLimitDeviation:
                        layer.changeAttributeValue(
                            id,
                            puAreaLimitDeviationFieldId,
                            puAreaLimitDeviation)
                    
                    originalPuAreaMaxQualityCode = feature.attribute(
                        puAreaMaxQualityCodeColumnName)
                    
                    if puAreaMaxQualityCode != originalPuAreaMaxQualityCode:
                        layer.changeAttributeValue(
                            id,
                            puAreaMaxQualityCodeFieldId,
                            puAreaMaxQualityCode)
                    
                    if puAreaAbsDifference > puAreaLimitDeviation:
                        exceededPuAreaLimitDeviationParIds.append(id)
            
            layer.commitChanges()
            
            if editing:
                self.iface.actionToggleEditing()
                
            layer.selectByIds(exceededPuAreaLimitDeviationParIds)
            
            featureCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featureCount == 0:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka nebyla překročena u žádné parcely.',
                    duration)
            elif featureCount == 1:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka byla překročena u {} parcely.'
                    .format(featureCount), duration)
            elif 1 < featureCount:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka byla překročena u {} parcel.'
                    .format(featureCount), duration)
        except self.dW.puError:
            QgsApplication.processEvents()
        except:
            QgsApplication.processEvents()
            
            currentCheckAnalysisName = \
                self.pW.checkAnalysisComboBox.currentText()
            
            self.dW.display_error_messages(
                self.pW,
                u'Error executing "{}".'.format(currentCheckAnalysisName),
                u'Chyba při provádění "{}".'.format(currentCheckAnalysisName))

    def _get_pu_area_max_quality_codes(self, layer, rowidColumnName):
        """Gets PU area maximum quality codes.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
            rowidColumnName (str): A name of rowid column.
        
        Returns:
            defaultdict: A defaultdict with rowids as keys (long)
                and PU area maximum quality codes as values (float).
        
        """

        sobrString = self.dW.sobrLayerCode
        spolString = self.dW.spolLayerCode
        
        sobrLayer = self._get_vertex_layer(layer, sobrString)
        spolLayer = self._get_vertex_layer(layer, spolString)
        
        parSobrLayer = self._get_joined_layer(layer, sobrLayer)
        parSpolLayer = self._get_joined_layer(layer, spolLayer)
        
        puAreaMaxQualityCodes = defaultdict(float)
        
        for parVertexLayer in (parSobrLayer, parSpolLayer):
            puAreaMaxQualityCodes = self._extract_pu_area_max_quality_codes(
                    parVertexLayer,
                    puAreaMaxQualityCodes,
                    rowidColumnName)
        
        return puAreaMaxQualityCodes
        
    def _get_vertex_layer(self, layer, vertexLayerCode):
        """Gets vertex layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
            vertexLayerCode (str): A code of the layer.
        
        Returns:
            QgsVectorLayer: A reference to the vertex layer of the given code.
        
        """
        
        parString = self.dW.parLayerCode
        
        layerSource = layer.source()
        layerName = layer.name()
        
        codeLayerSource = layerSource.replace(parString, vertexLayerCode)
        codeLayerName = layerName.replace(parString, vertexLayerCode)
        codeLayer = QgsVectorLayer(codeLayerSource, codeLayerName, 'ogr')
        
        return codeLayer
    
    def _get_joined_layer(self, layer, vertexLayer):
        """Gets joined layer.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
            vertexLayer (QgsVectorLayer): A reference to the vertex layer.
        
        Returns:
            QgsVectorLayer: A reference to the joined layer, None when layer
                or vertex layer has no feature.
        
        """
        
        selectedFeatureCount = layer.selectedFeatureCount()
        vertexLayerFeatureCount = vertexLayer.featureCount()
        
        parVertexLayer = None
        
        if selectedFeatureCount != 0 and vertexLayerFeatureCount != 0:
            parVertexLayerFilePath = processing.runalg(
                'qgis:joinattributesbylocation',
                layer, vertexLayer, u'touches', 0, 1, u'max', 0, None)['OUTPUT']
            
            vertexLayerCode = vertexLayer.name().split('|')[1]
            
            parVertexLayerName = layer.name() + u'-join-' + vertexLayerCode
            
            parVertexLayer = QgsVectorLayer(
                parVertexLayerFilePath, parVertexLayerName, 'ogr')
        
        return parVertexLayer
    
    def _extract_pu_area_max_quality_codes(
            self, vertexLayer, puAreaMaxQualityCodes, rowidColumnName):
        """Extracts PU area maximum quality codes.
        
        Args:
            vertexLayer (QgsVectorLayer): A reference to the vertex layer.
            puAreaMaxQualityCodes (defaultdict): A defaultdict
                with rowids as keys (long)
                and PU area maximum quality codes as values (float).
            rowidColumnName (str): A name of rowid column.
        
        Returns:
            defaultdict: A defaultdict with rowids as keys (long)
                and PU area maximum quality codes as values (float).
        
        """
        
        if vertexLayer:
            maxQualityCodeColumnName = u'maxKODCHB_'
            
            features = vertexLayer.getFeatures()
            
            for feature in features:
                rowid = feature.attribute(rowidColumnName)
                
                puAreaMaxQualityCode = feature.attribute(
                    maxQualityCodeColumnName)
                
                if type(puAreaMaxQualityCode) == QPyNullVariant:
                    continue
                
                if puAreaMaxQualityCode > puAreaMaxQualityCodes[rowid]:
                    puAreaMaxQualityCodes[rowid] = puAreaMaxQualityCode
        
        return puAreaMaxQualityCodes
    
    def _get_pu_area_limit_deviation(
            self, sgiArea, spiArea, puAreaMaxQualityCode):
        """Gets PU area limit deviation.
        
        Args:
            sgiArea (int): A SGI area.
            spiArea (int): A SPI area.
            puAreaMaxQualityCode (float): A PU area maximum quality code.
        
        Returns:
            float: A PU area limit deviation,
                None when limit deviation is not defined.
        
        """
        
        biggerArea = max(sgiArea, spiArea)
        
        if puAreaMaxQualityCode not in range(3, 9):
            limitDeviation = None
        elif puAreaMaxQualityCode == 3:
            limitDeviation = 2
        elif puAreaMaxQualityCode == 4:
            limitDeviation = 0.4*sqrt(biggerArea) + 4
        elif puAreaMaxQualityCode == 5:
            limitDeviation = 1.2*sqrt(biggerArea) + 12
        elif puAreaMaxQualityCode == 6:
            limitDeviation = 0.3*sqrt(biggerArea) + 3
        elif puAreaMaxQualityCode == 7:
            limitDeviation = 0.8*sqrt(biggerArea) + 8
        elif puAreaMaxQualityCode == 8:
            limitDeviation = 2.0*sqrt(biggerArea) + 20
        
        return round(limitDeviation)


class AreaLabelPuCaWidget(PuCaWidget):
    """A label widget for 'area' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass

