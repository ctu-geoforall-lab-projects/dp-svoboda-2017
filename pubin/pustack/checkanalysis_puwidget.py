# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CheckAnalysisPuWidget
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

from PyQt4.QtGui import (QGridLayout, QLabel, QComboBox, QStackedWidget,
                         QSizePolicy, QPushButton)
from PyQt4.QtCore import pyqtSignal, Qt

from qgis.core import *

from puwidget import PuWidget
from execute_thread import ExecuteThread
from puca import (perimeter_pucawidget, notinspi_pucawidget,
                  notinmap_pucawidget, area_pucawidget, unowned_pucawidget,
                  distance_pucawidget, bpej_pucawidget)


class CheckAnalysisPuWidget(PuWidget):
    """A widget with checks and analyzes."""
    
    set_text_statusbar = pyqtSignal(str, int)
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'checkAnalysisPuWidget')
        
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName(u'gridLayout')
        self.gridLayout.setColumnStretch(1, 1)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.set_text_statusbar.connect(self.dW.statusBar.set_text)
        
        self.checkAnalysisLabel = QLabel(self)
        self.checkAnalysisLabel.setObjectName(u'checkAnalysisLabel')
        self.checkAnalysisLabel.setText(u'Kontrola/analýza:')
        self.gridLayout.addWidget(
            self.checkAnalysisLabel, 0, 0, 1, 1)
        
        self.checkAnalysisComboBox = QComboBox(self)
        self.checkAnalysisComboBox.setObjectName(u'checkAnalysisComboBox')
        self.gridLayout.addWidget(
            self.checkAnalysisComboBox, 0, 1, 1, 1)
        
        perimeterString = u'kontrola - obvodem'
        self.checkAnalysisComboBox.addItem(perimeterString)
        self.checkAnalysisComboBox.setItemData(
            0, perimeterString, Qt.ToolTipRole)
        
        notInSpiString = u'kontrola - není v SPI'
        self.checkAnalysisComboBox.addItem(notInSpiString)
        self.checkAnalysisComboBox.setItemData(
            1, notInSpiString + u' (nová parcela)', Qt.ToolTipRole)
        
        notInMapString = u'kontrola - není v mapě'
        self.checkAnalysisComboBox.addItem(notInMapString)
        self.checkAnalysisComboBox.setItemData(
            2, notInMapString, Qt.ToolTipRole)
        
        areaString = u'kontrola - výměra nad mezní odchylkou'
        self.checkAnalysisComboBox.addItem(areaString)
        self.checkAnalysisComboBox.setItemData(
            3, areaString, Qt.ToolTipRole)
        
        unownedString = u'kontrola - bez vlastníka'
        self.checkAnalysisComboBox.addItem(unownedString)
        self.checkAnalysisComboBox.setItemData(
            4, unownedString + u' (pouze zjednodušená evidence)',
            Qt.ToolTipRole)
        
        distanceString = u'analýza - měření vzdálenosti'
        self.checkAnalysisComboBox.addItem(distanceString)
        self.checkAnalysisComboBox.setItemData(
            5, distanceString + u' (referenční bod - těžiště parcel)',
            Qt.ToolTipRole)
        
        bpejString = u'analýza - oceňování podle BPEJ'
        self.checkAnalysisComboBox.addItem(bpejString)
        self.checkAnalysisComboBox.setItemData(
            6, bpejString, Qt.ToolTipRole)
        
        self.gridLayout.setRowStretch(1, 1)
        
        self.checkAnalysisLabelStackedWidget = QStackedWidget(self)
        self.checkAnalysisLabelStackedWidget.setObjectName(
            u'checkAnalysisLabelStackedWidget')
        self.gridLayout.addWidget(
            self.checkAnalysisLabelStackedWidget, 2, 0, 1, 1)
        
        self.checkAnalysisStackedWidget = QStackedWidget(self)
        self.checkAnalysisStackedWidget.setObjectName(
            u'checkAnalysisStackedWidget')
        self.gridLayout.addWidget(
            self.checkAnalysisStackedWidget, 2, 1, 1, 1)
        
        self.perimeterLabelPuCaWidget = \
            perimeter_pucawidget.PerimeterLabelPuCaWidget(
                self, self.dWName, self.iface, self.dW, self.pluginDir,
                self.lockPlatform, u'perimeterLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(
            self.perimeterLabelPuCaWidget)
        self.perimeterPuCaWidget = perimeter_pucawidget.PerimeterPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'perimeterPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.perimeterPuCaWidget)
        
        self.notInSpiLabelPuCaWidget = \
            notinspi_pucawidget.NotInSpiLabelPuCaWidget(
                self, self.dWName, self.iface, self.dW, self.pluginDir,
                self.lockPlatform, u'notInSpiLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(
            self.notInSpiLabelPuCaWidget)
        self.notInSpiPuCaWidget = notinspi_pucawidget.NotInSpiPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'notInSpiPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.notInSpiPuCaWidget)
        
        self.notInMapLabelPuCaWidget = \
            notinmap_pucawidget.NotInMapLabelPuCaWidget(
                self, self.dWName, self.iface, self.dW, self.pluginDir,
                self.lockPlatform, u'notInMapLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(
            self.notInMapLabelPuCaWidget)
        self.notInMapPuCaWidget = notinmap_pucawidget.NotInMapPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'notInMapPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.notInMapPuCaWidget)
        
        self.areaLabelPuCaWidget = area_pucawidget.AreaLabelPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'areaLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(self.areaLabelPuCaWidget)
        self.areaPuCaWidget = area_pucawidget.AreaPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'areaPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.areaPuCaWidget)
        
        self.unownedLabelPuCaWidget = unowned_pucawidget.UnownedLabelPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'unownedLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(
            self.unownedLabelPuCaWidget)
        self.unownedPuCaWidget = unowned_pucawidget.UnownedPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'unownedPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.unownedPuCaWidget)
        
        self.distanceLabelPuCaWidget = \
            distance_pucawidget.DistanceLabelPuCaWidget(
                self, self.dWName, self.iface, self.dW, self.pluginDir,
                self.lockPlatform, u'distanceLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(
            self.distanceLabelPuCaWidget)
        self.distancePuCaWidget = distance_pucawidget.DistancePuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'distancePuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.distancePuCaWidget)
        
        self.bpejLabelPuCaWidget = bpej_pucawidget.BpejLabelPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'bpejLabelPuCaWidget')
        self.checkAnalysisLabelStackedWidget.addWidget(self.bpejLabelPuCaWidget)
        self.bpejPuCaWidget = bpej_pucawidget.BpejPuCaWidget(
            self, self.dWName, self.iface, self.dW, self.pluginDir,
            self.lockPlatform, u'bpejPuCaWidget')
        self.checkAnalysisStackedWidget.addWidget(self.bpejPuCaWidget)
        
        self.checkAnalysisComboBox.currentIndexChanged.connect(
            self.checkAnalysisLabelStackedWidget.setCurrentIndex)
        self.checkAnalysisComboBox.currentIndexChanged.connect(
            self.checkAnalysisStackedWidget.setCurrentIndex)
        self.checkAnalysisComboBox.currentIndexChanged.connect(
            self._set_text_checkAnalysisPushButton)
        
        self.gridLayout.setRowStretch(3, 1)
        
        self.checkAnalysisPushButton = QPushButton(self)
        self.checkAnalysisPushButton.setObjectName(u'checkAnalysisPushButton')
        self.checkAnalysisPushButton.clicked.connect(self._run_check)
        self.checkAnalysisPushButton.setText(
            u'Provést kontrolu a vybrat problémové parcely')
        self.gridLayout.addWidget(
            self.checkAnalysisPushButton, 4, 0, 1, 2)
    
    def _run_check(self):
        """Starts the current check or analysis.
        
        First it calls a function that checks if there is an active layer
        and if the active layer contains all required columns. If that function
        returns True, check or analysis is executed in a separate thread.
        
        """
        
        succes, layer = self.dW.check_layer(self)
        
        if succes:
            self.executeThread = ExecuteThread(layer)
            self.executeThread.started.connect(
                self.checkAnalysisStackedWidget.currentWidget().execute)
            self.executeThread.start()
    
    def _set_text_checkAnalysisPushButton(self, currentIndex):
        """Sets checkAnalysisPushButton's text.
        
        Sets checkAnalysisPushButton's text according to checkAnalysisComboBox's
        current index.
        
        Args:
            currentIndex (int): Current index of the checkAnalysisComboBox.
        
        """
        
        if currentIndex <= 4:
            self.checkAnalysisPushButton.setText(
                u'Provést kontrolu a vybrat problémové parcely')
        else:
            self.checkAnalysisPushButton.setText(
                u'Provést analýzu')

