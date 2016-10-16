# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ui_DockWidget
                                 A QGIS plugin
 Plugin pro pozemkové úpravy
                              -------------------
        begin                : 2016-10-15
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

from PyQt4 import QtCore
from PyQt4.QtGui import (QWidget, QGridLayout, QFrame, QHBoxLayout, QLabel,
                         QLineEdit, QPushButton, QProgressBar, QToolBar,
                         QAction, QIcon, QPixmap)

from retranslate_ui import _fromUtf8, _translate


class ui_DockWidget(object):
    """TODO"""

    def setup_ui(self, dockWidget):
        dockWidget.setObjectName(_fromUtf8('dockWidget'))
        
        self.mainWidget = QWidget(dockWidget)
        self.mainWidget.setObjectName(_fromUtf8('mainWidget'))
        
        dockWidget.setWidget(self.mainWidget)
        
        self.mainGridLayout = QGridLayout(self.mainWidget)
        self.mainGridLayout.setObjectName(_fromUtf8('mainGridLayout'))
        
        self.loadVfkFrame = QFrame(self.mainWidget)
        self.loadVfkFrame.setObjectName(_fromUtf8('loadVfkFrame'))
        self.loadVfkFrame.setFrameShape(QFrame.StyledPanel)
        self.loadVfkFrame.setFrameShadow(QFrame.Raised)
        self.mainGridLayout.addWidget(self.loadVfkFrame, 1, 0, 1, 1)
        
        self.loadVfkGridLayout = QGridLayout(self.loadVfkFrame)
        self.loadVfkGridLayout.setObjectName(_fromUtf8('loadVfkGridLayout'))
        
        self.browseVfkHBoxLayout = QHBoxLayout(self.loadVfkFrame)
        self.browseVfkHBoxLayout.setObjectName(
            _fromUtf8('browseVfkHBoxLayout'))
        self.loadVfkGridLayout.addLayout(self.browseVfkHBoxLayout, 0, 0, 1, 3)
        
        self.browseVfkLabel = QLabel(self.loadVfkFrame)
        self.browseVfkLabel.setObjectName(_fromUtf8('browseVfkLabel'))
        self.browseVfkHBoxLayout.addWidget(self.browseVfkLabel)
        
        self.browseVfkLineEdit = QLineEdit(self.loadVfkFrame)
        self.browseVfkLineEdit.setObjectName(_fromUtf8('browseVfkLineEdit'))
        self.browseVfkHBoxLayout.addWidget(self.browseVfkLineEdit)
        
        self.browseVfkPushButton = QPushButton(self.loadVfkFrame)
        self.browseVfkPushButton.setObjectName(_fromUtf8('browseVfkPushButton'))
        self.browseVfkHBoxLayout.addWidget(self.browseVfkPushButton)
        
        self.loadVfkHBoxLayout = QHBoxLayout(self.loadVfkFrame)
        self.loadVfkHBoxLayout.setObjectName(_fromUtf8('loadVfkHBoxLayout'))
        self.loadVfkGridLayout.addLayout(self.loadVfkHBoxLayout, 1, 0, 1, 3)
        
        self.loadVfkProgressBar = QProgressBar(self.loadVfkFrame)
        self.loadVfkProgressBar.setObjectName(_fromUtf8('loadVfkProgressBar'))
        self.loadVfkProgressBar.setValue(0)
        self.loadVfkHBoxLayout.addWidget(self.loadVfkProgressBar)
        
        self.loadVfkPushButton = QPushButton(self.loadVfkFrame)
        self.loadVfkPushButton.setObjectName(_fromUtf8('loadVfkPushButton'))
        self.loadVfkHBoxLayout.addWidget(self.loadVfkPushButton)
        
        self.statusLabel = QLabel(self.loadVfkFrame)
        self.statusLabel.setObjectName(_fromUtf8('statusLabel'))
        self.mainGridLayout.addWidget(self.statusLabel, 2, 0, 1, 1)
        
        self.actionGroupWidget = QWidget(self.mainWidget)
        self.actionGroupWidget.setObjectName(_fromUtf8('actionGroupWidget'))
        self.mainGridLayout.addWidget(self.actionGroupWidget, 0, 0, 1, 1)
        
        self.actionGroupHBoxLayout = QHBoxLayout(self.actionGroupWidget)
        self.actionGroupHBoxLayout.setObjectName(
            _fromUtf8('actionGroupHBoxLayout'))
        
        self.actionGroup = QToolBar(self.actionGroupWidget)
        self.actionGroupHBoxLayout.addWidget(self.actionGroup)
        
        self.selectRectangleAction = QAction(self.actionGroupWidget)
        self.selectRectangleAction.setObjectName(_fromUtf8('selectRectangleAction'))
        selectRectangleIcon = QIcon()
        selectRectangleIcon.addPixmap(
            QPixmap(_fromUtf8(':/mActionSelectRectangle.svg')),
            QIcon.Normal, QIcon.On)
        self.selectRectangleAction.setIcon(selectRectangleIcon)
        self.actionGroup.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = QAction(self.actionGroupWidget)
        self.selectPolygonAction.setObjectName(_fromUtf8('selectPolygonAction'))
        selectPolygonIcon = QIcon()
        selectPolygonIcon.addPixmap(
            QPixmap(_fromUtf8(':/mActionSelectPolygon.svg')),
            QIcon.Normal, QIcon.On)
        self.selectPolygonAction.setIcon(selectPolygonIcon)
        self.actionGroup.addAction(self.selectPolygonAction)
        
        self._retranslateUi(dockWidget)
        
        QtCore.QMetaObject.connectSlotsByName(dockWidget)
 
    def _retranslateUi(self, dockWidget):
        dockWidget.setWindowTitle(_translate('dockWidget', 'PU Plugin', None))
        
        self.browseVfkLabel.setText(_translate(
            'dockWidget', u'VFK soubor:', None))
        
        self.browseVfkPushButton.setText(_translate(
            'dockWidget', u'Procházet', None))
        
        self.statusLabel.setText(_translate(
            'dockWidget', u'Vyberte VFK soubor.', None))
        
        self.loadVfkPushButton.setText(_translate(
            'dockWidget', u'Načíst', None))
        
