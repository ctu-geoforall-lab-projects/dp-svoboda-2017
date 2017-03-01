# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NotInSpiPuCaWidget and NotInSpiLabelPuCaWidget
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


class NotInSpiPuCaWidget(PuCaWidget):
    """A widget for 'not in SPI' check."""
    
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
                u'Provádím kontrolu - není v SPI...', 0)
            
            expression = QgsExpression(
                "\"{}\" is null".format(self.dW.requiredColumnsPAR[7]))
            
            self.dW.select_features_by_expression(layer, expression)
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featuresCount == 0:
                self.pW.set_text_statusbar.emit(
                    u'V SPI jsou všechny parcely.', duration)
            elif featuresCount == 1:
                self.pW.set_text_statusbar.emit(
                    u'V SPI není {} parcela.'.format(featuresCount), duration)
            elif 1 < featuresCount < 5:
                self.pW.set_text_statusbar.emit(
                    u'V SPI nejsou {} parcely.'.format(featuresCount), duration)
            elif 5 <= featuresCount:
                self.pW.set_text_statusbar.emit(
                    u'V SPI není {} parcel.'.format(featuresCount), duration)
        except self.dW.puError:
            QgsApplication.processEvents()
        except:
            QgsApplication.processEvents()
            
            currentCheckAnalysisName = \
                self.pW.checkAnalysisComboBox.currentText()
            
            self.dW.display_error_messages(
                u'Error executing "{}".'.format(currentCheckAnalysisName),
                u'Chyba při provádění "{}".'.format(currentCheckAnalysisName))


class NotInSpiLabelPuCaWidget(PuCaWidget):
    """A label widget for 'not in SPI' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass
