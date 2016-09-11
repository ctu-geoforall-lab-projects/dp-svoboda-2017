# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoadVfkClass
                                 A QGIS plugin
 Plugin pro pozemkové úpravy
                             -------------------
        begin                : 2016-09-04
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

from PyQt4.QtCore import QObject, QFileInfo, QDir, QUuid, pyqtSignal
from PyQt4.QtSql import QSqlDatabase

from qgis.core import *
from qgis.gui import QgsMessageLogViewer, QgsMessageBar
from qgis.utils import iface

from osgeo import ogr

import traceback


class LoadVfkClass(QObject):
    """A class for loading VFK file."""
    
    def __init__(self, _filePath, loadVfkLabel, loadVfkFileProgressBar,
                 vfkFileLineEdit, vfkFileBrowseButton, loadVfkFileButton):
        """Constructor.
        
        Args:
            _filePath (str): A full path to the file.
            loadVfkLabel (QLabel): The label that displays loading messages.
            loadVfkFileProgressBar (QProgressBar): The loading progress bar.
            vfkFileLineEdit (QLineEdit): The line edit with path to the file.
            vfkFileBrowseButton (QPushButton): The push button for browsing.
            loadVfkFileButton (QPushButton): The push button for loading.
        
        """
        
        super(LoadVfkClass, self).__init__()
        
        self._filePath = _filePath
        self.loadVfkLabel = loadVfkLabel
        self.loadVfkFileProgressBar = loadVfkFileProgressBar
        self.vfkFileLineEdit = vfkFileLineEdit
        self.vfkFileBrowseButton = vfkFileBrowseButton
        self.loadVfkFileButton = loadVfkFileButton
    
    def run_loading_vfk_layer(self):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        """
        
        self._enable_load_widgets(False)
        
        self.loadVfkFileProgressBar.setValue(0)
        
        _fileInfo = QFileInfo(self._filePath)
        _dbName = QDir(
            _fileInfo.absolutePath()).filePath(_fileInfo.baseName() + '.db')
        
        self._load_vfk_file()
        self._open_database(_dbName)
        
        _vfkLayerCode = 'PAR'
        _layerName = _fileInfo.baseName() + '-' + _vfkLayerCode
        
        self._load_vfk_layer(_vfkLayerCode, _layerName)
        
        self._enable_load_widgets(True)
    
    def _load_vfk_file(self):
        """Loads a VFK file.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            QgsApplication.registerOgrDrivers()
            QgsApplication.processEvents()
            
            _ogrDataSource = ogr.Open(self._filePath)
            
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
    
    def _load_vfk_layer(self, _vfkLayerCode, _layerName):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Also sets symbology according
        to "/plugins/puPlugin/data/<_vfkLayerCode>.qml" file.
        
        Args:
            _vfkLayerCode (str): A code of the layer.
            _layerName (str): A name of the layer.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, loadVfkLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            _composedURI = self._filePath + "|layername=" + _vfkLayerCode
            _layer = QgsVectorLayer(_composedURI, _layerName, 'ogr')
            
            if _layer.isValid():
                _style = ':/plugins/puPlugin/data/' + _vfkLayerCode + '.qml'
                _layer.loadNamedStyle(_style)
                QgsMapLayerRegistry.instance().addMapLayer(_layer)
            else:
                self._raise_load_error(
                    'Layer {} is not valid'.format(_vfkLayerCode),
                    u'Vrstva {} není platná'.format(_vfkLayerCode))
        except:
            self._raise_load_error(
                    'Error loading {} layer'.format(_vfkLayerCode),
                    u'Chyba při načítání vrsty {}'.format(_vfkLayerCode))
    
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
        
