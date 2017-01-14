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
        self.distanceGridLayout.addWidget(
            self.refPointMapLayerComboBox, 0, 1, 1, 1)
        
        self.distanceGridLayout.setColumnStretch(1, 1)
    
    def execute(self, layer):
        """Executes the analysis.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            editing = self.dW.check_editing()
            
            refPointLayer = self.refPointMapLayerComboBox.currentLayer()
            
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
                u'Provádím analýzu - měření vzdálenosti.', 0)
            
            refPointFeatures = refPointLayer.getFeatures()
            
            for feature in refPointFeatures:
                refPoint = feature.geometry().asPoint()
            
            fieldID = layer.fieldNameIndex('PU_VZDALENOST')
            
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
            
            if editing == True:
                self.dW.stackedWidget.editFrame.toggleEditingAction.trigger()
            
            self.pW.set_text_statusbar.emit(
                u'Analýza měření vzdálenosti úspěšně dokončena.', 20)
        except:
            currentAnalysisName = self.pW.checkAnalysisComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing "{}".'.format(currentAnalysisName),
                u'Chyba při provádění "{}".'.format(currentAnalysisName))

