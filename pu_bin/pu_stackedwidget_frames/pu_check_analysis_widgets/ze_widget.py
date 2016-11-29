# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ZeWidget
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

from PyQt4.QtGui import QWidget

from qgis.core import *


class ZeWidget(QWidget):
    """A widget for 'ZE' check."""
    
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
        
        super(ZeWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'zeWidget')
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            self.pW.text_statusbar.emit(
                u'Provádím kontrolu - bez vlastníka '
                u'(pouze zjednodušená evidence).', 0)
            
            fieldName = 'ID'
            
            layer.removeSelection()
            
            expression = QgsExpression("\"PAR_TYPE\" = 'PKN'")
            
            features = layer.getFeatures(QgsFeatureRequest(expression))
            
            pknFeaturesID = [feature.attribute(fieldName) for feature in features]
            
            featuresID = []
            
            expression = QgsExpression("\"PAR_TYPE\" = 'PZE'")
            
            features = layer.getFeatures(QgsFeatureRequest(expression))
            
            for feature in features:
                featureVfkID = feature.attribute(fieldName)
                
                if featureVfkID not in pknFeaturesID:
                    featuresID.append(feature.id())
            
            layer.selectByIds(featuresID)
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10000
            
            if featuresCount == 0:
                self.pW.text_statusbar.emit(
                    u'Bez vlastníka není žádná parcela.', duration)
            elif featuresCount == 1:
                self.pW.text_statusbar.emit(
                    u'Bez vlastníka je {} parcela.'.format(featuresCount), duration)
            elif 1 < featuresCount < 5:
                self.pW.text_statusbar.emit(
                    u'Bez vlastníka jsou {} parcely.'.format(featuresCount),
                    duration)
            elif 5 <= featuresCount:
                self.pW.text_statusbar.emit(
                    u'Bez vlastníka je {} parcel.'.format(featuresCount), duration)
        except:
            currentCheckName = self.pW.checkAnalysisComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing "{}".'.format(currentCheckName),
                u'Chyba při provádění "{}".'.format(currentCheckName))
