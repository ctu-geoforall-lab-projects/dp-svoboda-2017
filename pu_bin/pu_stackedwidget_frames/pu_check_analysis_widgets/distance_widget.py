# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DistanceWidget
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

from PyQt4.QtGui import QWidget, QLabel, QGridLayout
from PyQt4.QtCore import Qt

from qgis.gui import QgsMapLayerComboBox, QgsMapLayerProxyModel
from qgis.core import *

import processing
from math import sqrt


class DistanceWidget(QWidget):
    """A widget for 'distance' analysis."""
    
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
        self.lastRefPointLayer = None
        
        super(DistanceWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'distanceWidget')
        
        self.distanceGridLayout = QGridLayout(self)
        self.distanceGridLayout.setObjectName(u'distanceGridLayout')
        self.distanceGridLayout.setAlignment(Qt.AlignTop)
        self.distanceGridLayout.setContentsMargins(0, 0, 0, 0)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.refPointLabel = QLabel(self)
        self.refPointLabel.setObjectName(u'refPointLabel')
        self.refPointLabel.setText(u'Referenční bod:')
        self.distanceGridLayout.addWidget(self.refPointLabel, 0, 0, 1, 1)
        
        self.refPointMapLayerComboBox = QgsMapLayerComboBox(self)
        self.refPointMapLayerComboBox.setObjectName(
            u'refPointMapLayerComboBox')
        self.refPointMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PointLayer)
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._rollback_ref_point_layer)
        QgsMapLayerRegistry.instance().layersRemoved.connect(
            self._reset_ref_point_layer)
        self.set_ref_point_layer(self.lastRefPointLayer)
        self.distanceGridLayout.addWidget(
            self.refPointMapLayerComboBox, 0, 1, 1, 1)
        
        self.distanceGridLayout.setColumnStretch(1, 1)
    
    def set_ref_point_layer(self, refPointLayer):
        """Sets the reference point layer in the refPointMapLayerComboBox.
        
        Args:
            refPointLayer (QgsVectorLayer): A reference to the reference
                point layer.
        
        """
        
        self.lastRefPointLayer = refPointLayer
        
        self.refPointMapLayerComboBox.setLayer(refPointLayer)
    
    def _reset_ref_point_layer(self):
        """Resets the reference point layer."""
        
        layers = self.iface.legendInterface().layers()
        
        if self.lastRefPointLayer not in layers:
            self.set_ref_point_layer(None)
    
    def _rollback_ref_point_layer(self):
        """Rollbacks the reference point layer."""
        
        if self.lastRefPointLayer == None:
            self.refPointMapLayerComboBox.setLayer(self.lastRefPointLayer)
        else:
            self.lastRefPointLayer = \
                self.refPointMapLayerComboBox.currentLayer()
    
    def execute(self, layer):
        """Executes the analysis.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        editing = self.dW.check_editing()
        
        refPointLayer = self.refPointMapLayerComboBox.currentLayer()
        
        if refPointLayer == None:
            self.pW.set_text_statusbar.emit(
                u'Žádná vrstva referenčního bodu.', 10)
            return
        
        refPointCount = refPointLayer.featureCount()
        
        refPointLayerCrs = refPointLayer.crs().authid()
        layerCrs = layer.crs().authid()
        
        if refPointLayerCrs != layerCrs:
            self.pW.set_text_statusbar.emit(
                u'Aktivní vrstva a vrstva referenčního bodu nemají stejný '
                u'souřadnicový systém.', 10)
            return
        
        if refPointCount != 1:
            self.pW.set_text_statusbar.emit(
                u'Vrstva referenčního bodu neobsahuje právě jeden prvek.',
                10)
            return
        
        if layer.selectedFeatureCount() != 0:
            features = layer.selectedFeaturesIterator()
        else:
            features = layer.getFeatures()
        
        self.pW.set_text_statusbar.emit(
            u'Provádím analýzu - měření vzdálenosti...', 0)
        
        refPointFeatures = refPointLayer.getFeatures()
        
        for feature in refPointFeatures:
            refPoint = feature.geometry().asPoint()
        
        fieldID = layer.fieldNameIndex(self.dW.visiblePuColumnsPAR[3])
        
        layer.startEditing()
        layer.updateFields()
        
        for feature in features:
            featureGeometry = feature.geometry()
            
            if featureGeometry != None:
                featureID = feature.id()
                
                featureCentroid = featureGeometry.centroid().asPoint()
                distanceDouble = sqrt(refPoint.sqrDist(featureCentroid))
                distance = int(round(distanceDouble))
                
                layer.changeAttributeValue(featureID, fieldID, distance)
        
        layer.commitChanges()
        
        if editing:
            self.dW.stackedWidget.editFrame.toggleEditingAction.trigger()
        
        self.pW.set_text_statusbar.emit(
            u'Analýza měření vzdálenosti úspěšně dokončena.', 20)
    
    def _set_refPoint_layer(self):
        """Sets current reference point layer.
        
        Sets current reference point layer to None if the last reference point
        layer was None.
        
        """
        
        if self.lastRefPointLayer == None:
            self.refPointMapLayerComboBox.setLayer(self.lastRefPointLayer)
        else:
            self.lastRefPointLayer = \
                self.refPointMapLayerComboBox.currentLayer()

