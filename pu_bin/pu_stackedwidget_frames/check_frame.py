# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CheckFrame
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

from PyQt4.QtGui import (QFrame, QGridLayout, QHBoxLayout, QLabel, QComboBox,
                         QStackedWidget, QPushButton)
from PyQt4.QtCore import pyqtSignal

from pu_check_analysis_widgets import (perimeter_widget, notinspi_widget,
                                       notinmap_widget, area_widget,
                                       distance_widget)


class CheckFrame(QFrame):
    """A frame which contains widgets for checks."""
    
    text_statusbar = pyqtSignal(str, int)
    
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
        
        super(QFrame, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'checkFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.text_statusbar.connect(self.dW.statusbar._set_text_statusbar)
        
        self.checkGridLayout = QGridLayout(self)
        self.checkGridLayout.setObjectName(u'checkGridLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.checkHBoxLayout = QHBoxLayout(self)
        self.checkHBoxLayout.setObjectName(u'checkHBoxLayout')
        self.checkGridLayout.addLayout(self.checkHBoxLayout, 0, 0, 1, 2)
        
        self.checkLabel = QLabel(self)
        self.checkLabel.setObjectName(u'checkLabel')
        self.checkLabel.setText(u'Kontrola/analýza:')
        self.checkHBoxLayout.addWidget(self.checkLabel)
        
        self.checkComboBox = QComboBox(self)
        self.checkComboBox.setObjectName(u'checkComboBox')
        self.checkComboBox.addItem(u'kontrola - obvodem')
        self.checkComboBox.addItem(u'kontrola - není v SPI (nová parcela)')
        self.checkComboBox.addItem(u'kontrola - není v mapě')
        self.checkComboBox.addItem(u'kontrola - výměra nad mezní odchylkou')
        self.checkComboBox.addItem(
            u'analýza - měření vzdálenosti (referenční bod - těžiště parcel)')

        self.checkHBoxLayout.addWidget(self.checkComboBox, 1)
        
        self.checkStackedWidget = QStackedWidget(self)
        self.checkStackedWidget.setObjectName(u'checkStackedWidget')
        self.checkGridLayout.addWidget(self.checkStackedWidget, 1, 0, 1, 2)
        
        self.perimeterWidget = perimeter_widget.PerimeterWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.perimeterWidget)
        
        self.notInSpiWidget = notinspi_widget.NotInSpiWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.notInSpiWidget)
        
        self.notInMapWidget = notinmap_widget.NotInMapWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.notInMapWidget)
        
        self.areaWidget = area_widget.AreaWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.areaWidget)
        
        self.distanceWidget = distance_widget.DistanceWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.distanceWidget)
        
        self.checkComboBox.currentIndexChanged.connect(
            self.checkStackedWidget.setCurrentIndex)
        self.checkComboBox.currentIndexChanged.connect(
            self._set_text_checkPushButton)
        
        self.checkPushButton = QPushButton(self)
        self.checkPushButton.setObjectName(u'checkPushButton')
        self.checkPushButton.clicked.connect(self._run_check)
        self.checkPushButton.setText(
            u'Provést kontrolu a vybrat problémové parcely')
        self.checkGridLayout.addWidget(self.checkPushButton, 2, 0, 1, 2)
    
    def _run_check(self):
        """Starts current check.
        
        First it calls a function that checks if there is an active layer
        and if the active layer contains all required columns. If that function
        returns True, check is executed.
        
        """
        
        try:
            succes, layer = self.pW.check_active_layer(self)
            
            if succes == True:
                self.checkStackedWidget.currentWidget().execute(layer)
        except:
            currentCheckName = self.checkComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing check "{}".'.format(currentCheckName),
                u'Chyba při provádění kontroly "{}".'.format(currentCheckName))
    
    def _set_text_checkPushButton(self, currentIndex):
        """Sets checkPushButton's text.
        
        Sets checkPushButton's text according to checkComboBox's current index.
        
        Args:
            currentIndex (int): Current index of the checkComboBox.
        
        """
        
        if currentIndex <= 3:
            self.checkPushButton.setText(
                u'Provést kontrolu a vybrat problémové parcely')
        else:
            self.checkPushButton.setText(
                u'Provést analýzu')

