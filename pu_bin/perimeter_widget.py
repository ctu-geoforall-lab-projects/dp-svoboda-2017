# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PerimeterWidget
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


class PerimeterWidget(QWidget):
    """A widget for 'perimeter' check."""
    
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
        
        self.setObjectName(u'perimeterWidget')
        
        self.perimeterHBoxLayout = QHBoxLayout(self)
        self.perimeterHBoxLayout.setObjectName(u'perimeterHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.perimeterLabel = QLabel(self)
        self.perimeterLabel.setObjectName(u'perimeterLabel')
        self.perimeterLabel.setText(u'Obvod:')
        self.perimeterHBoxLayout.addWidget(self.perimeterLabel)
        
        self.mapLayerComboBox = QgsMapLayerComboBox(self)
        self.mapLayerComboBox.setObjectName(u'mapLayerComboBox')
        self.mapLayerComboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.perimeterHBoxLayout.addWidget(self.mapLayerComboBox, 1)
    
    def execute(self):
        """Executes the check."""
        
        layer = self.iface.activeLayer()
        
        if not layer:
            self.pW.text_statusbar.emit(u'Žádná aktivní vrstva.', 7000)
            return
        
        if layer.type() != 0:
            self.pW.text_statusbar.emit(u'Aktivní vrstva není vektorová.', 7000)
            return
        
        perimeter = self.mapLayerComboBox.currentLayer()
        
        processing.runalg(
            'qgis:selectbylocation', layer, perimeter, u'within', 0, 0)
        
        layer.invertSelection()
        
        featuresCount = layer.selectedFeatureCount()
        
        duration = 10000
        
        if featuresCount == 0:
            self.pW.text_statusbar.emit(
                u'Uvnitř obvodu jsou všechny parcely.', duration)
        elif featuresCount == 1:
            self.pW.text_statusbar.emit(
                u'Uvnitř obvodu není {} parcela'.format(featuresCount), duration)
        elif 1 < featuresCount < 5:
            self.pW.text_statusbar.emit(
                u'Uvnitř obvodu nejsou {} parcely.'.format(featuresCount), duration)
        elif 5 <= featuresCount:
            self.pW.text_statusbar.emit(
                u'Uvnitř obvodu není {} parcel.'.format(featuresCount), duration)

