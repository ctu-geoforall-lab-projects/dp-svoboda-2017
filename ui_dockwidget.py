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
                         QLineEdit, QPushButton, QProgressBar)

from retranslate_ui import _fromUtf8, _translate


class ui_DockWidget(object):
    """TODO"""

    def setup_ui(self, dockWidget):
        dockWidget.setObjectName(_fromUtf8("dockWidget"))
        
        self.mainWidget = QWidget(dockWidget)
        self.mainWidget.setObjectName(_fromUtf8("mainWidget"))
        
        dockWidget.setWidget(self.mainWidget)
        
        self.mainGridLayout = QGridLayout(self.mainWidget)
        self.mainGridLayout.setObjectName(_fromUtf8("mainGridLayout"))
        
        self.loadVfkFrame = QFrame(self.mainWidget)
        self.loadVfkFrame.setObjectName(_fromUtf8("loadVfkFrame"))
        self.loadVfkFrame.setFrameShape(QFrame.StyledPanel)
        self.loadVfkFrame.setFrameShadow(QFrame.Raised)
        self.mainGridLayout.addWidget(self.loadVfkFrame, 1, 0, 1, 1)
        
        self.loadVfkGridLayout = QGridLayout(self.loadVfkFrame)
        self.loadVfkGridLayout.setObjectName(_fromUtf8("loadVfkGridLayout"))
        
        self.browseVfkHBoxLayout = QHBoxLayout(self.mainWidget)
        self.browseVfkHBoxLayout.setObjectName(
            _fromUtf8("browseVfkHBoxLayout"))
        self.loadVfkGridLayout.addLayout(self.browseVfkHBoxLayout, 0, 0, 1, 3)
        
        self.browseVfkLabel = QLabel(self.mainWidget)
        self.browseVfkLabel.setObjectName(_fromUtf8("browseVfkLabel"))
        self.loadVfkGridLayout.addWidget(self.browseVfkLabel, 0, 0, 1, 1)
        
        self.browseVfkLineEdit = QLineEdit(self.mainWidget)
        self.browseVfkLineEdit.setObjectName(_fromUtf8("browseVfkLineEdit"))
        self.loadVfkGridLayout.addWidget(self.browseVfkLineEdit, 0, 1, 1, 1)
        
        self.browseVfkPushButton = QPushButton(self.mainWidget)
        self.browseVfkPushButton.setObjectName(_fromUtf8("browseVfkPushButton"))
        self.loadVfkGridLayout.addWidget(self.browseVfkPushButton, 0, 2, 1, 1)
        
        self.loadVfkLabel = QLabel(self.mainWidget)
        self.loadVfkLabel.setObjectName(_fromUtf8("loadVfkLabel"))
        self.loadVfkGridLayout.addWidget(self.loadVfkLabel, 1, 0, 1, 3)
        
        self.loadVfkHBoxLayout = QHBoxLayout(self.mainWidget)
        self.loadVfkHBoxLayout.setObjectName(_fromUtf8("loadVfkHBoxLayout"))
        self.loadVfkGridLayout.addLayout(self.browseVfkHBoxLayout, 2, 0, 1, 3)
        
        self.loadVfkProgressBar = QProgressBar(self.mainWidget)
        self.loadVfkProgressBar.setObjectName(_fromUtf8("loadVfkProgressBar"))
        self.loadVfkProgressBar.setValue(0)
        self.loadVfkGridLayout.addWidget(self.loadVfkProgressBar, 2, 0, 1, 2)
        
        self.loadVfkPushButton = QPushButton(self.mainWidget)
        self.loadVfkPushButton.setObjectName(_fromUtf8("loadVfkPushButton"))
        self.loadVfkGridLayout.addWidget(self.loadVfkPushButton, 2, 2, 1, 1)
        
        self._retranslateUi(dockWidget)
        
        QtCore.QMetaObject.connectSlotsByName(dockWidget)
 
    def _retranslateUi(self, dockWidget):
        dockWidget.setWindowTitle(_translate("dockWidget", "PU Plugin", None))
        
        self.browseVfkLabel.setText(_translate(
            "dockWidget", u'VFK soubor:', None))
        
        self.browseVfkPushButton.setText(_translate(
            "dockWidget", u'Procházet', None))
        
        self.loadVfkLabel.setText(_translate(
            "dockWidget", u'Vyberte VFK soubor.', None))
        
        self.loadVfkPushButton.setText(_translate(
            "dockWidget", u'Načíst', None))
        
