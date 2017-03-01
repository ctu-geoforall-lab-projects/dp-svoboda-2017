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

from pucawidget import PuCaWidget


class AreaPuCaWidget(PuCaWidget):
    """A widget for 'area' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.areaLineEdit = QLineEdit(self)
        self.areaLineEdit.setObjectName(u'areaLineEdit')
        doubleValidator = QDoubleValidator(self.areaLineEdit)
        doubleValidator.setBottom(0)
        self.areaLineEdit.setValidator(doubleValidator)
        self.vBoxLayout.addWidget(self.areaLineEdit)
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer (QgsVectorLayer): A reference to the active layer.
        
        """
        
        try:
            editing = self.dW.check_editing()
            
            threshold = self.areaLineEdit.text()
            
            if not threshold:
                self.pW.set_text_statusbar.emit(
                    u'Není zadána mezní odchylka.', 10)
                return
            
            self.pW.set_text_statusbar.emit(
                u'Provádím kontrolu - výměra nad mezní odchylkou.', 0)
            
            fieldID = layer.fieldNameIndex('PU_VYMERA_PARCELY')
            
            layer.startEditing()
            layer.updateFields()
            
            problematicParcelsID = []
            
            features = layer.getFeatures()
            
            for feature in features:
                featureGeometry = feature.geometry()
                if featureGeometry == None:
                    continue
                
                sgiArea = int(round(featureGeometry.area()))
                spiArea = feature.attribute('VYMERA_PARCELY')
                
                if sgiArea != spiArea:
                    featureID = feature.id()
                    layer.changeAttributeValue(featureID, fieldID, sgiArea)
                    
                    if type(spiArea) == QPyNullVariant:
                        continue
                    
                    limitDifference =  spiArea*(float(threshold)/100)
                    
                    if abs(sgiArea - spiArea) > limitDifference:
                        problematicParcelsID.append(featureID)
            
            layer.commitChanges()
            
            if editing:
                self.iface.actionToggleEditing()
                
            layer.selectByIds(problematicParcelsID)
            
            featuresCount = layer.selectedFeatureCount()
            
            duration = 10
            
            if featuresCount == 0:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka nebyla překročena u žádné parcely.',
                    duration)
            elif featuresCount == 1:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka byla překročena u {} parcely.'
                    .format(featuresCount), duration)
            elif 1 < featuresCount:
                self.pW.set_text_statusbar.emit(
                    u'Mezní odchylka byla překročena u {} parcel.'
                    .format(featuresCount), duration)
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


class AreaLabelPuCaWidget(PuCaWidget):
    """A label widget for 'area' check."""
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.areaLabel = QLabel(self)
        self.areaLabel.setObjectName(u'areaLabel')
        self.areaLabel.setText(u'Mezní odchylka [%]:')
        self.vBoxLayout.addWidget(self.areaLabel)

