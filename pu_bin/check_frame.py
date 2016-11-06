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
        # self.checkComboBox.addItem(u'obvodem')
        # self.checkComboBox.addItem(u'není v SPI (nová parcela)')
        self.checkComboBox.addItem(u'není v mapě')
        self.checkComboBox.addItem(u'výměra nad mezní odchylkou')
        self.checkHBoxLayout.addWidget(self.checkComboBox, 1)
        
        self.checkStackedWidget = QStackedWidget(self)
        self.checkStackedWidget.setObjectName(u'checkStackedWidget')
        self.checkGridLayout.addWidget(self.checkStackedWidget, 1, 0, 1, 2)
        
        self.checkPushButton = QPushButton(self)
        self.checkPushButton.setObjectName(u'checkPushButton')
        self.checkPushButton.setText(u'Provést kontrolu')
        self.checkGridLayout.addWidget(self.checkPushButton, 2, 0, 1, 2)

