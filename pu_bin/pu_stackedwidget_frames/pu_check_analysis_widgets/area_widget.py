# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AreaWidget
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

from PyQt4.QtGui import (QWidget, QHBoxLayout, QLabel, QLineEdit,
                         QDoubleValidator)
from PyQt4.QtCore import QPyNullVariant


class AreaWidget(QWidget):
    """A widget for 'area' check."""
    
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
        
        self.setObjectName(u'areaWidget')
        
        self.areaHBoxLayout = QHBoxLayout(self)
        self.areaHBoxLayout.setObjectName(u'areaHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.areaLabel = QLabel(self)
        self.areaLabel.setObjectName(u'areaLabel')
        self.areaLabel.setText(u'Mezní odchylka [%]:')
        self.areaHBoxLayout.addWidget(self.areaLabel)
        
        self.areaLineEdit = QLineEdit(self)
        self.areaLineEdit.setObjectName(u'areaLineEdit')
        doubleValidator = QDoubleValidator(self.areaLineEdit)
        doubleValidator.setBottom(0)
        self.areaLineEdit.setValidator(doubleValidator)
        self.areaHBoxLayout.addWidget(self.areaLineEdit, 1)
    
    def execute(self, layer):
        """Executes the check.
        
        Args:
            layer(QgsVectorLayer): A reference to the active layer.
        
        """
        
        if self.dW.stackedWidget.editFrame.toggleEditingAction.isChecked():
            editing = True
        else:
            editing = False
        
        threshhold = self.areaLineEdit.text()
        
        if not threshhold:
            self.pW.text_statusbar.emit(
                u'Není zadána mezní odchylka.', 7000)
            return
        
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
                fieldID = layer.fieldNameIndex('PU_VYMERA_PARCELY')
                layer.changeAttributeValue(featureID, fieldID, sgiArea)
                
                if type(spiArea) == QPyNullVariant:
                    continue
                
                limitDifference =  spiArea*(float(threshhold)/100)
                
                if abs(sgiArea - spiArea) > limitDifference:
                    problematicParcelsID.append(featureID)
        
        layer.commitChanges()
        
        if editing == True:
            self.dW.stackedWidget.editFrame.toggleEditingAction.trigger()
            
        layer.selectByIds(problematicParcelsID)
        
        featuresCount = layer.selectedFeatureCount()
        
        duration = 10000
        
        if featuresCount == 0:
            self.pW.text_statusbar.emit(
                u'Mezní odchylka nebyla překročena u žádné parcely.', duration)
        elif featuresCount == 1:
            self.pW.text_statusbar.emit(
                u'Mezní odchylka byla překročena u {} parcely.'
                .format(featuresCount), duration)
        elif 1 < featuresCount:
            self.pW.text_statusbar.emit(
                u'Mezní odchylka byla překročena u {} parcel.'
                .format(featuresCount), duration)

