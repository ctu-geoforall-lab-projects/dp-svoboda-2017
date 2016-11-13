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

from perimeter_widget import PerimeterWidget
from notinmap_widget import NotInMapWidget
from notinspi_widget import NotInSpiWidget
from area_widget import AreaWidget


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
        self.checkLabel.setText(u'Kontrola:')
        self.checkHBoxLayout.addWidget(self.checkLabel)
        
        self.checkComboBox = QComboBox(self)
        self.checkComboBox.setObjectName(u'checkComboBox')
        self.checkComboBox.addItem(u'obvodem')
        self.checkComboBox.addItem(u'není v SPI (nová parcela)')
        self.checkComboBox.addItem(u'není v mapě')
        self.checkComboBox.addItem(u'výměra nad mezní odchylkou')

        self.checkHBoxLayout.addWidget(self.checkComboBox, 1)
        
        self.checkStackedWidget = QStackedWidget(self)
        self.checkStackedWidget.setObjectName(u'checkStackedWidget')
        self.checkGridLayout.addWidget(self.checkStackedWidget, 1, 0, 1, 2)
        
        self.perimeterWidget = PerimeterWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.perimeterWidget)
        
        self.notInSpiWidget = NotInSpiWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.notInSpiWidget)
        
        self.notInMapWidget = NotInMapWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.notInMapWidget)
        
        self.areaWidget = AreaWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkStackedWidget.addWidget(self.areaWidget)
        
        self.checkComboBox.currentIndexChanged.connect(
            self.checkStackedWidget.setCurrentIndex)
        
        self.checkPushButton = QPushButton(self)
        self.checkPushButton.setObjectName(u'checkPushButton')
        self.checkPushButton.clicked.connect(self._run_check)
        self.checkPushButton.setText(
            u'Provést kontrolu a vybrat problémové parcely')
        self.checkGridLayout.addWidget(self.checkPushButton, 2, 0, 1, 2)
    
    def _run_check(self):
        """Starts current check.
        
        First it check if there is an active layer, then if the active layer
        contains all required columns and then it executes the check.
        
        """
        
        try:
            layer = self.iface.activeLayer()
            
            if not layer:
                self.text_statusbar.emit(u'Žádná aktivní vrstva.', 7000)
                return
            
            fieldNames = [field.name() for field in layer.pendingFields()]
            
            if not all(column in fieldNames for column in self.pW.rqdColumnsPAR):
                self.text_statusbar.emit(
                    u'Aktivní vrstva neobsahuje potřebné sloupce.', 7000)
                return
            
            self.checkStackedWidget.currentWidget().execute(layer)
        except:
            currentCheckName = self.checkComboBox.currentText()
            
            raise self.dW.puError(
                self.dW,
                u'Error executing check "{}".'.format(currentCheckName),
                u'Chyba při provádění kontroly "{}".'.format(currentCheckName))

