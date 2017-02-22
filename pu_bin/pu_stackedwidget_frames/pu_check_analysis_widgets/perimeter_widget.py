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

from PyQt4.QtGui import QWidget, QLabel, QGridLayout
from PyQt4.QtCore import Qt

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
        self.lastPerimeterLayer = None
        
        super(PerimeterWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'perimeterWidget')
        
        self.perimeterGridLayout = QGridLayout(self)
        self.perimeterGridLayout.setObjectName(u'perimeterGridLayout')
        self.perimeterGridLayout.setAlignment(Qt.AlignTop)
        self.perimeterGridLayout.setContentsMargins(0, 0, 0, 0)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.perimeterLabel = QLabel(self)
        self.perimeterLabel.setObjectName(u'perimeterLabel')
        self.perimeterLabel.setText(u'Obvod:')
        self.perimeterGridLayout.addWidget(self.perimeterLabel, 0, 0, 1, 1)
        
        self.perimeterMapLayerComboBox = QgsMapLayerComboBox(self)
        self.perimeterMapLayerComboBox.setObjectName(
            u'perimeterMapLayerComboBox')
        self.perimeterMapLayerComboBox.setFilters(
            QgsMapLayerProxyModel.PolygonLayer)
        self.perimeterMapLayerComboBox.activated.connect(
            self._sync_perimeter_map_layer_combo_box)
        QgsMapLayerRegistry.instance().layersAdded.connect(
            self._rollback_perimeter_layer)
        QgsMapLayerRegistry.instance().layersRemoved.connect(
            self._reset_perimeter_layer)
        self.set_perimeter_layer(self.lastPerimeterLayer)
        self.perimeterGridLayout.addWidget(
            self.perimeterMapLayerComboBox, 0, 1, 1, 1)
        
        self.perimeterGridLayout.setColumnStretch(1, 1)
    
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
    
    def _sync_perimeter_map_layer_combo_box(self):
        """Synchronizes perimeter map layer combo boxes.
        
        Synchronizes with the perimeterMapLayerComboBox in the editFrame.
        
        """
        
        perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
        
        if perimeterLayer != self.lastPerimeterLayer:
            self.lastPerimeterLayer = perimeterLayer
            
            self.dW.stackedWidget.editFrame.set_perimeter_layer(perimeterLayer)
    
    def _reset_perimeter_layer(self):
        """Resets the perimeter layer."""
        
        layers = self.iface.legendInterface().layers()
        
        if self.lastPerimeterLayer not in layers:
            self.set_perimeter_layer(None)
    
    def _rollback_perimeter_layer(self):
        """Rollbacks the perimeter layer."""
        
        if self.lastPerimeterLayer == None:
            self.set_perimeter_layer(self.lastPerimeterLayer, False)
        else:
            self.lastPerimeterLayer = \
                self.perimeterMapLayerComboBox.currentLayer()
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        perimeterLayer = self.perimeterMapLayerComboBox.currentLayer()
        
        if not self.dW.check_perimeter_layer(perimeterLayer, layer, True):
            return
        
        self.pW.set_text_statusbar.emit(u'Provádím kontrolu - obvodem...', 0)
        
        processing.runalg(
            'qgis:selectbylocation',
            layer, perimeterLayer, u'within', 0, 0)
        
        layer.invertSelection()
            
        features = layer.selectedFeaturesIterator()
        
        featuresCount = layer.selectedFeatureCount()
        
        duration = 10
        
        if featuresCount == 0:
            self.pW.set_text_statusbar.emit(
                u'Uvnitř obvodu jsou všechny parcely.', duration)
        elif featuresCount == 1:
            self.pW.set_text_statusbar.emit(
                u'Uvnitř obvodu není {} parcela'.format(featuresCount),
                duration)
        elif 1 < featuresCount < 5:
            self.pW.set_text_statusbar.emit(
                u'Uvnitř obvodu nejsou {} parcely.'.format(featuresCount),
                duration)
        elif 5 <= featuresCount:
            self.pW.set_text_statusbar.emit(
                u'Uvnitř obvodu není {} parcel.'.format(featuresCount),
                duration)

