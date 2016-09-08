# -*- coding: utf-8 -*-
"""
/***************************************************************************
 puPluginDockWidget
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

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt4.QtGui import QFileDialog

from qgis.core import *

from open_thread import OpenThread
from load_vfk_class import LoadVfkClass
from fileinput import filename

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pu_plugin_dockwidget_base.ui'))


class puPluginDockWidget(QtGui.QDockWidget, FORM_CLASS):
    """The main widget of the PU Plugin."""
    
    closingPlugin = pyqtSignal()
    
    def __init__(self, parent=None):
        """Default constructor."""
        
        super(puPluginDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
    
    @pyqtSlot()
    def on_vfkFileBrowseButton_clicked(self):
        """Opens a file dialog and filters VFK files."""
        
        _filePath = QFileDialog.getOpenFileName(
            self, u'Načti soubor VFK',
            self.vfkFileLineEdit.text(),
            'VFK soubor (*.vfk)')
        
        if not _filePath:
            return
        
        self.vfkFileLineEdit.setText(_filePath)
    
    @pyqtSlot()
    def on_loadVfkFileButton_clicked(self):
        """Starts loading the selected VFK file in a separate thread."""
        
        _filePath = self.vfkFileLineEdit.text()
        
        QgsApplication.processEvents()
        
        self.loadVfkClass = LoadVfkClass(
            _filePath, self.loadVfkLabel, self.loadVfkFileProgressBar)
        
        self.openThread = OpenThread()
        self.openThread.work.connect(self.loadVfkClass.run_loading_vfk_layer)
        self.openThread.start()
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

