# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NotInMapPuCaWidget and NotInMapLabelPuCaWidget
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

from qgis.core import *

from pucawidget import PuCaWidget


class NotInMapPuCaWidget(PuCaWidget):
    """A widget for 'not in map' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            self.pW.set_text_statusbar.emit(
                u'Provádím kontrolu - není v mapě...', 0)
            
            expression = QgsExpression("$geometry is null")
            
            self.dW.select_features_by_expression(layer, expression)
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featuresCount == 0:
                self.pW.set_text_statusbar.emit(
                    u'V mapě jsou všechny parcely.', duration)
            elif featuresCount == 1:
                self.pW.set_text_statusbar.emit(
                    u'V mapě není {} parcela.'.format(featuresCount), duration)
            elif 1 < featuresCount < 5:
                self.pW.set_text_statusbar.emit(
                    u'V mapě nejsou {} parcely.'.format(featuresCount),
                    duration)
            elif 5 <= featuresCount:
                self.pW.set_text_statusbar.emit(
                    u'V mapě není {} parcel.'.format(featuresCount), duration)
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


class NotInMapLabelPuCaWidget(PuCaWidget):
    """A label widget for 'not in map' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass

