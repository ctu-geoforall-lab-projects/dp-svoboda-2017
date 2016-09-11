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

from fileinput import filename

import traceback
import threading


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
    
    @pyqtSlot()
    def on_vfkFileBrowseButton_clicked(self):
        """Opens a file dialog and filters VFK files."""
        
        _filePath = QFileDialog.getOpenFileName(
            self, u'Vyberte soubor VFK',
            self.vfkFileLineEdit.text(),
            '.vfk (*.vfk)')
        
        if not _filePath:
            return
        
        self.vfkFileLineEdit.setText(_filePath)
    
    @pyqtSlot()
    def on_loadVfkFileButton_clicked(self):
        """Starts loading the selected VFK file in a separate thread."""
        
        _filePath = self.vfkFileLineEdit.text()
        
        self.loadVfkLabel.setText(u'Načítám data do SQLite databáze.')
        
        self._enable_load_widgets(False)
        
        QgsApplication.processEvents()
        
        threading.Thread(target=self.run_loading_vfk_layer(_filePath)).start()
    
    def on_vfkFileLineEdit_textChanged(self):
        """Checks if the text in vfkFileLineEdit is a path to valid VFK file.
        
        If so, loadVfkFileButton is enabled, otherwise loadVfkFileButton
        is disabled.
        """
        
        _tempText = self.vfkFileLineEdit.text()
        
        _tempFilePath = QFileInfo(_tempText)
         
        if _tempFilePath.isFile() and _tempFilePath.suffix() in ('vfk', 'VFK'): 
            self.loadVfkFileButton.setEnabled(True)
        else:
            self.loadVfkFileButton.setEnabled(False)
            
    def run_loading_vfk_layer(self, _filePath):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        
        Args:
            _filePath (str): A full path to the file.
        
        """
        
        self.loadVfkFileProgressBar.setValue(0)
        
        _fileInfo = QFileInfo(_filePath)
        _dbName = QDir(
            _fileInfo.absolutePath()).filePath(_fileInfo.baseName() + '.db')
        
        self._load_vfk_file(_filePath)
        self._open_database(_dbName)
        
        _vfkLayerCode = 'PAR'
        _layerName = _fileInfo.baseName() + '-' + _vfkLayerCode
        
        self._load_vfk_layer(_filePath, _vfkLayerCode, _layerName)
        
        self._enable_load_widgets(True)
    
    def _load_vfk_file(self, _filePath):
        """Loads a VFK file.
        
        Args:
            _filePath (str): A full path to the file.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            QgsApplication.registerOgrDrivers()
            QgsApplication.processEvents()
            
            _ogrDataSource = ogr.Open(_filePath)
            
            _layerCount = _ogrDataSource.GetLayerCount()
            _layerNames = []
            
            for i in xrange(_layerCount):
                _layerNames.append(
                    _ogrDataSource.GetLayer(i).GetLayerDefn().GetName())
            
            if 'PAR' not in _layerNames:
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
            
            self.loadVfkFileProgressBar.setRange(0, _layerCount)
            
            for i in xrange(_layerCount):
                self.loadVfkFileProgressBar.setValue(i+1)
                self.loadVfkLabel.setText(
                    u"Načítám {} ({}/{})"
                    .format(_layerNames[i], i+1, _layerCount))
                
                QgsApplication.processEvents()
                
            self.loadVfkLabel.setText(u'Data byla úspešně načtena.')
        except:
            self._raise_load_error(
                'Error loading VFK file.',
                u'Chyba při načítání VFK souboru.')
    
    def _open_database(self, _dbName):
        """Opens a database.
        
        Args:
            _dbName (QDir): A full path to the database.
        
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
            
            _connectionName = QUuid.createUuid().toString()
            _db = QSqlDatabase.addDatabase("QSQLITE", _connectionName)
            _db.setDatabaseName(_dbName)
            
            if not _db.open():
                self._raise_load_error(
                    'Database connection failed.',
                    u'Nepodařilo se připojit k databázi.')
        except:
            self._raise_load_error(
                'Error opening database connection.',
                u'Chyba při otevírání databáze.')
    
    def _load_vfk_layer(self, _filePath, _vfkLayerCode, _layerName):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Also sets symbology according
        to "/plugins/puPlugin/data/<_vfkLayerCode>.qml" file.
        
        Args:
            _filePath (str): A full path to the file.
            _vfkLayerCode (str): A code of the layer.
            _layerName (str): A name of the layer.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            _composedURI = _filePath + "|layername=" + _vfkLayerCode
            _layer = QgsVectorLayer(_composedURI, _layerName, 'ogr')
            
            if _layer.isValid():
                _style = ':/plugins/puPlugin/data/' + _vfkLayerCode + '.qml'
                _layer.loadNamedStyle(_style)
                QgsMapLayerRegistry.instance().addMapLayer(_layer)
            else:
                self._raise_load_error(
                    'Layer {} is not valid.'.format(_vfkLayerCode),
                    u'Vrstva {} není platná.'.format(_vfkLayerCode))
        except:
            self._raise_load_error(
                    'Error loading {} layer.'.format(_vfkLayerCode),
                    u'Chyba při načítání vrsty {}.'.format(_vfkLayerCode))
    
    def _raise_load_error(
            self, _engLogMsg, _czeLabelMsg, _czeBarMsg=None, _duration=7):
        """Displays error messages.
        
        Displays error messages in the 'puPlugin' Log Messages Panel,
        loadVfkLabel and Message Bar.
        
        For development purposes it displays traceback
        in the 'puPlugin Development' Log Messages Tab.
        
        Args:
            _engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            _czeLabelMsg (str): A message in the loadVfkLabel.
            _czeLabelMsg (str): A message in the Message Bar.
            _duration (int): A duration of the message in the Message Bar
                             in seconds.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        _pluginName = 'PU Plugin'
        
        if _czeBarMsg is None:
            _czeBarMsg = _czeLabelMsg
        
        QgsMessageLog.logMessage(_engLogMsg, _pluginName)
        self.loadVfkLabel.setText(_czeLabelMsg)
        iface.messageBar().pushMessage(
            _pluginName, _czeBarMsg , QgsMessageBar.WARNING, _duration)
        
        _developmentTb = 'PU Plugin Development'
        _tb = traceback.format_exc()
        
        if 'None' not in _tb:
            QgsMessageLog.logMessage(_tb, _developmentTb)
            
    def _enable_load_widgets(self, _enableBool):
        """Sets enabled or disabled loading widgets.
        
        Sets enabled or disabled following widgets:
            vfkFileLineEdit
            vfkFileBrowseButton
            loadVfkFileButton 
        
        Args:
            _enableBool (bool): True to set enabled, False to set disabled.
        
        """
        
        self.vfkFileLineEdit.setEnabled(_enableBool)
        self.vfkFileBrowseButton.setEnabled(_enableBool)
        self.loadVfkFileButton.setEnabled(_enableBool)
    
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

