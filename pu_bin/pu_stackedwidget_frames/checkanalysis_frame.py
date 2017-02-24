# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CheckAnalysisFrame
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
from PyQt4.QtCore import pyqtSignal, Qt

from pu_checkanalysis_widgets import (perimeter_widget, notinspi_widget,
                                       notinmap_widget, ze_widget, area_widget,
                                       distance_widget, bpej_widget)

from execute_thread import ExecuteThread


class CheckAnalysisFrame(QFrame):
    """A frame which contains widgets for checks and analyzes."""
    
    set_text_statusbar = pyqtSignal(str, int)
    
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
        
        super(CheckAnalysisFrame, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'checkFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.set_text_statusbar.connect(self.dW.statusBar.set_text_statusbar)
        
        self.checkAnalysisGridLayout = QGridLayout(self)
        self.checkAnalysisGridLayout.setObjectName(u'checkAnalysisGridLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.checkAnalysisHBoxLayout = QHBoxLayout(self)
        self.checkAnalysisHBoxLayout.setObjectName(u'checkAnalysisHBoxLayout')
        self.checkAnalysisGridLayout.addLayout(
            self.checkAnalysisHBoxLayout, 0, 0, 1, 2)
        
        self.checkAnalysisLabel = QLabel(self)
        self.checkAnalysisLabel.setObjectName(u'checkAnalysisLabel')
        self.checkAnalysisLabel.setText(u'Kontrola/analýza:')
        self.checkAnalysisHBoxLayout.addWidget(self.checkAnalysisLabel)
        
        self.checkAnalysisComboBox = QComboBox(self)
        self.checkAnalysisComboBox.setObjectName(u'checkAnalysisComboBox')
        
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
        
        zeString = u'kontrola - bez vlastníka'
        self.checkAnalysisComboBox.addItem(zeString)
        self.checkAnalysisComboBox.setItemData(
            4, zeString + u' (pouze zjednodušená evidence)',
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

        self.checkAnalysisHBoxLayout.addWidget(self.checkAnalysisComboBox, 1)
        
        self.checkAnalysisStackedWidget = QStackedWidget(self)
        self.checkAnalysisStackedWidget.setObjectName(
            u'checkAnalysisStackedWidget')
        self.checkAnalysisGridLayout.addWidget(
            self.checkAnalysisStackedWidget, 1, 0, 1, 2)
        
        self.perimeterWidget = perimeter_widget.PerimeterWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.perimeterWidget)
        
        self.notInSpiWidget = notinspi_widget.NotInSpiWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.notInSpiWidget)
        
        self.notInMapWidget = notinmap_widget.NotInMapWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.notInMapWidget)
        
        self.areaWidget = area_widget.AreaWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.areaWidget)
        
        self.zeWidget = ze_widget.ZeWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.zeWidget)
        
        self.distanceWidget = distance_widget.DistanceWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.distanceWidget)
        
        self.bpejWidget = bpej_widget.BpejWidget(
            self, self.dWName, self.iface, self.dW)
        self.checkAnalysisStackedWidget.addWidget(self.bpejWidget)
        
        self.checkAnalysisComboBox.currentIndexChanged.connect(
            self.checkAnalysisStackedWidget.setCurrentIndex)
        self.checkAnalysisComboBox.currentIndexChanged.connect(
            self._set_text_checkAnalysisPushButton)
        
        self.checkAnalysisGridLayout.setRowStretch(2, 1)
        
        self.checkAnalysisPushButton = QPushButton(self)
        self.checkAnalysisPushButton.setObjectName(u'checkAnalysisPushButton')
        self.checkAnalysisPushButton.clicked.connect(self._run_check)
        self.checkAnalysisPushButton.setText(
            u'Provést kontrolu a vybrat problémové parcely')
        self.checkAnalysisGridLayout.addWidget(
            self.checkAnalysisPushButton, 3, 0, 1, 2)
    
    def _run_check(self):
        """Starts current check or analysis.
        
        First it calls a function that checks if there is an active layer
        and if the active layer contains all required columns. If that function
        returns True, check or analysis is executed in a separate thread.
        
        """
        
        succes, layer = self.dW.check_layer(self)
        
        if succes:
            self.executeThread = ExecuteThread(layer)
            self.executeThread.work.connect(
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

