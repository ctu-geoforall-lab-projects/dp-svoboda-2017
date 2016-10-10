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
from PyQt4.QtCore import pyqtSignal, pyqtSlot, QThread, QFileInfo, QDir, QUuid
from PyQt4.QtGui import QFileDialog
from PyQt4.QtSql import QSqlDatabase

from qgis.core import *
from qgis.gui import QgsMessageBar
from qgis.utils import iface

from osgeo import ogr

import traceback
import threading

from load_thread import LoadThread


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pu_plugin_dockwidget_base.ui'))


class puPluginDockWidget(QtGui.QDockWidget, FORM_CLASS):
    """The main widget of the PU Plugin."""
    
    closingPlugin = pyqtSignal()
    
    def __init__(self, parent=None):
        """Constructor."""
        
        super(puPluginDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.loadVfkFileButton.setDisabled(True)
        
        self.vfkFileBrowseButton.clicked.connect(
            self.vfkFileBrowseButton_clicked)
        self.loadVfkFileButton.clicked.connect(
            self.loadVfkFileButton_clicked)
    
    def vfkFileBrowseButton_clicked(self):
        """Opens a file dialog and filters VFK files."""
        
        filePath = QFileDialog.getOpenFileName(
            self, u'Vyberte soubor VFK',
            self.vfkFileLineEdit.text(),
            '.vfk (*.vfk)')
        
        if not filePath:
            return
        
        self.vfkFileLineEdit.setText(filePath)
    
    def loadVfkFileButton_clicked(self):
        """Starts loading the selected VFK file in a separate thread."""
        
        filePath = self.vfkFileLineEdit.text()
        
        self.loadVfkLabel.setText(u'Načítám data do SQLite databáze.')
        
        self._enable_load_widgets(False)
        
        QgsApplication.processEvents()
        
        self.loadThread = LoadThread(filePath)
        self.loadThread.work.connect(self.run_loading_vfk_layer)
        self.loadThread.start()
    
    def on_vfkFileLineEdit_textChanged(self):
        """Checks if the text in vfkFileLineEdit is a path to valid VFK file.
        
        If so, loadVfkFileButton is enabled, otherwise loadVfkFileButton
        is disabled.
        """
        
        tempText = self.vfkFileLineEdit.text()
        
        tempFilePath = QFileInfo(tempText)
         
        if tempFilePath.isFile() and tempFilePath.suffix() in ('vfk', 'VFK'): 
            self.loadVfkFileButton.setEnabled(True)
        else:
            self.loadVfkFileButton.setEnabled(False)
            
    def run_loading_vfk_layer(self, filePath):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        
        Args:
            filePath (str): A full path to the file.
        
        """
        
        self.loadVfkFileProgressBar.setValue(0)
        
        fileInfo = QFileInfo(filePath)
        dbName = QDir(
            fileInfo.absolutePath()).filePath(fileInfo.baseName() + '.db')
        
        self._load_vfk_file(filePath)
        self._open_database(dbName)
        
        vfkLayerCode = 'PAR'
        layerName = fileInfo.baseName() + '-' + vfkLayerCode
        
        self._load_vfk_layer(filePath, vfkLayerCode, layerName)
        
        self._enable_load_widgets(True)
    
    def _load_vfk_file(self, filePath):
        """Loads a VFK file.
        
        Args:
            filePath (str): A full path to the file.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            QgsApplication.registerOgrDrivers()
            QgsApplication.processEvents()
            
            ogrDataSource = ogr.Open(filePath)
            
            layerCount = ogrDataSource.GetLayerCount()
            layerNames = []
            
            for i in xrange(layerCount):
                layerNames.append(
                    ogrDataSource.GetLayer(i).GetLayerDefn().GetName())
            
            if 'PAR' not in layerNames:
                self._raise_load_error(
                    'VFK file does not contain PAR layer, therefore it '
                    'can not be loaded by PU Plugin. '
                    'The file can be loaded by "Add Vector Layer"',
                    u'VFK soubor neobsahuje vrstvu parcel.',
                    u'VFK soubor neobsahuje vrstvu parcel, '
                    u'proto nemůže být pomocí PU Pluginu načten. '
                    u'Data je možné načíst pomocí "Přidat vektorovou vrstvu."')
                QgsApplication.processEvents()
                return
            
            self.loadVfkFileProgressBar.setRange(0, layerCount)
            
            for i in xrange(layerCount):
                self.loadVfkFileProgressBar.setValue(i+1)
                self.loadVfkLabel.setText(
                    u"Načítám {} ({}/{})"
                    .format(layerNames[i], i+1, layerCount))
                
                QgsApplication.processEvents()
                
            self.loadVfkLabel.setText(u'Data byla úspešně načtena.')
        except:
            self._raise_load_error(
                'Error loading VFK file.',
                u'Chyba při načítání VFK souboru.')
    
    def _open_database(self, dbName):
        """Opens a database.
        
        Args:
            dbName (QDir): A full path to the database.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            if not QSqlDatabase.isDriverAvailable('QSQLITE'):
                self._raise_load_error(
                    'SQLITE database driver is not available.',
                    u'Databázový ovladač QSQLITE není dostupný.')
                return
            
            connectionName = QUuid.createUuid().toString()
            db = QSqlDatabase.addDatabase("QSQLITE", connectionName)
            db.setDatabaseName(dbName)
            
            if not db.open():
                self._raise_load_error(
                    'Database connection failed.',
                    u'Nepodařilo se připojit k databázi.')
        except:
            self._raise_load_error(
                'Error opening database connection.',
                u'Chyba při otevírání databáze.')
    
    def _load_vfk_layer(self, filePath, vfkLayerCode, layerName):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Also sets symbology according
        to "/plugins/puPlugin/data/<vfkLayerCode>.qml" file.
        
        Args:
            filePath (str): A full path to the file.
            vfkLayerCode (str): A code of the layer.
            layerName (str): A name of the layer.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            composedURI = filePath + "|layername=" + vfkLayerCode
            layer = QgsVectorLayer(composedURI, layerName, 'ogr')
            
            if layer.isValid():
                style = ':/plugins/puPlugin/data/' + vfkLayerCode + '.qml'
                layer.loadNamedStyle(style)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
            else:
                self._raise_load_error(
                    'Layer {} is not valid.'.format(vfkLayerCode),
                    u'Vrstva {} není platná.'.format(vfkLayerCode))
        except:
            self._raise_load_error(
                    'Error loading {} layer.'.format(vfkLayerCode),
                    u'Chyba při načítání vrsty {}.'.format(vfkLayerCode))
    
    def _raise_load_error(
            self, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
        """Displays error messages.
        
        Displays error messages in the 'puPlugin' Log Messages Panel,
        loadVfkLabel and Message Bar.
        
        For development purposes it displays traceback
        in the 'puPlugin Development' Log Messages Tab.
        
        Args:
            engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            czeLabelMsg (str): A message in the loadVfkLabel.
            czeLabelMsg (str): A message in the Message Bar.
            duration (int): A duration of the message in the Message Bar
                             in seconds.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        pluginName = 'PU Plugin'
        
        if czeBarMsg is None:
            czeBarMsg = czeLabelMsg
        
        QgsMessageLog.logMessage(engLogMsg, pluginName)
        self.loadVfkLabel.setText(czeLabelMsg)
        iface.messageBar().pushMessage(
            pluginName, czeBarMsg , QgsMessageBar.WARNING, duration)
        
        developmentTb = 'PU Plugin Development'
        tb = traceback.format_exc()
        
        if 'None' not in tb:
            QgsMessageLog.logMessage(tb, developmentTb)
            
    def _enable_load_widgets(self, enableBool):
        """Sets enabled or disabled loading widgets.
        
        Sets enabled or disabled following widgets:
            vfkFileLineEdit
            vfkFileBrowseButton
            loadVfkFileButton 
        
        Args:
            enableBool (bool): True to set enabled, False to set disabled.
        
        """
        
        self.vfkFileLineEdit.setEnabled(enableBool)
        self.vfkFileBrowseButton.setEnabled(enableBool)
        self.loadVfkFileButton.setEnabled(enableBool)
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

