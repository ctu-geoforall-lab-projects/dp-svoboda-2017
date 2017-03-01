# -*- coding: utf-8 -*-
"""
/***************************************************************************
 UnownedPuCaWidget and UnownedLabelPuCaWidget
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


class UnownedPuCaWidget(PuCaWidget):
    """A widget for 'unowned' check."""
    
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
                u'Provádím kontrolu - bez vlastníka...', 0)
            
            layer.removeSelection()
            
            expression = QgsExpression("\"TEL_ID\" is null")
            
            self.dW.select_features_by_expression(layer, expression)
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featuresCount == 0:
                self.pW.set_text_statusbar.emit(
                    u'Bez vlastníka není žádná parcela.', duration)
            elif featuresCount == 1:
                self.pW.set_text_statusbar.emit(
                    u'Bez vlastníka je {} parcela.'.format(featuresCount),
                    duration)
            elif 1 < featuresCount < 5:
                self.pW.set_text_statusbar.emit(
                    u'Bez vlastníka jsou {} parcely.'.format(featuresCount),
                    duration)
            elif 5 <= featuresCount:
                self.pW.set_text_statusbar.emit(
                    u'Bez vlastníka je {} parcel.'.format(featuresCount),
                    duration)
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


class UnownedLabelPuCaWidget(PuCaWidget):
    """A label widget for 'unowned' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        pass