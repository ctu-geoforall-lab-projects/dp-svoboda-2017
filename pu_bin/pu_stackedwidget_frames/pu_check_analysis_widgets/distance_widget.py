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

from PyQt4.QtGui import QWidget, QLabel, QHBoxLayout

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
        
        super(QWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'distanceWidget')
        
        self.distanceHBoxLayout = QHBoxLayout(self)
        self.distanceHBoxLayout.setObjectName(u'distanceHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.distanceLabel = QLabel(self)
        self.distanceLabel.setObjectName(u'distanceLabel')
        self.distanceLabel.setText(u'Referenční bod:')
        self.distanceHBoxLayout.addWidget(self.distanceLabel)
        
        self.distanceMapLayerComboBox = QgsMapLayerComboBox(self)
        self.distanceMapLayerComboBox.setObjectName(
            u'distanceMapLayerComboBox')
        self.distanceMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PointLayer)
        self.distanceHBoxLayout.addWidget(self.distanceMapLayerComboBox, 1)
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer(QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            if self.dW.stackedWidget.editFrame.toggleEditingAction.isChecked():
                editing = True
            else:
                editing = False
            
            refPointLayer = self.distanceMapLayerComboBox.currentLayer()
            
            refPointCount = refPointLayer.featureCount()
            
            refPointLayerCrs = refPointLayer.crs().authid()
            layerCrs = layer.crs().authid()
            
            if refPointLayerCrs != layerCrs:
                self.pW.text_statusbar.emit(
                    u'Aktivní vrstva a vrstva referenčního bodu nemají stejný '
                    u'souřadnicový systém.', 7000)
                return
            
            if refPointCount != 1:
                self.pW.text_statusbar.emit(
                    u'Vrstva referenčního bodu neobsahuje právě jeden prvek.',
                    7000)
                return
            
            self.pW.text_statusbar.emit(
                u'Provádím analýzu - měření vzdálenosti '
                u'(referenční bod - těžiště parcel).', 0)
            
            refPointFeatures = refPointLayer.getFeatures()
            
            for feature in refPointFeatures:
                refPoint = feature.geometry().asPoint()
            
            fieldID = layer.fieldNameIndex('PU_VZDALENOST')
            
            layer.startEditing()
            layer.updateFields()
            
            features = layer.getFeatures()
            
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
            
            self.pW.text_statusbar.emit(
                u'Analýza měření vzdáleností úspěšně dokončena.', 15000)
        except:
            currentCheckName = self.pW.checkComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing "{}".'.format(currentCheckName),
                u'Chyba při provádění "{}".'.format(currentCheckName))

