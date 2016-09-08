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


class LoadVfkClass(QObject):
    """A class for loading VFK file."""
    
    def __init__(self, _filePath, loadVfkLabel, loadVfkFileProgressBar):
        """Constructor.
        
        Args:
            _filePath (str): A full path to the file.
            loadVfkLabel (QLabel): The label that displays loading messages.
            loadVfkFileProgressBar (QProgressBar): The loading progress bar.
        """
        
        super(LoadVfkClass, self).__init__()
        
        self._filePath = _filePath
        self.loadVfkLabel = loadVfkLabel
        self.loadVfkFileProgressBar = loadVfkFileProgressBar
    
    def run_loading_vfk_layer(self):
        """Calls methods for loading a VFK layer."""

        self.loadVfkLabel.setText(u'Načítám data do SQLite databáze.')
        
        _fileInfo = QFileInfo(self._filePath)
        _dbName = QDir(
            _fileInfo.absolutePath()).\
            filePath(_fileInfo.baseName() + '.db')
        
        self._load_vfk_file(self._filePath, _dbName)
        
        self._open_database(_dbName)
        
        self._load_vfk_layer('PAR', self._filePath)
    
    def _load_vfk_file(self, _filePath, _dbName):
        """Loads a VFK file.
        
        Args:
            _filePath (str): A full path to the file.
            _dbName (QDir): A full path to the database.
        
        """
        try:
            QgsApplication.registerOgrDrivers()
            QgsApplication.processEvents()
            
            self.loadVfkFileProgressBar.setValue(0)
            
            _ogrDataSource = ogr.Open(_filePath)
            
            if not _ogrDataSource:
                self._raise_load_error(
                    'VFK file can not be loaded as a valid data source.' \
                    'If the file "{}" exists, try to delete it and load' \
                    'the data again.',
                    u'VFK soubor nelze otevřít jako platný datový zdroj.',
                    u'VFK soubor nelze otevřít jako platný datový zdroj.\
                    Pokud existuje soubor "{}", zkuste ho smazat\
                    a načíst data znovu.'.format(_dbName), 10)
            
            _layerCount = _ogrDataSource.GetLayerCount()
            _layerNames = []
            
            for i in xrange(_layerCount):
                _layerNames.append(
                    _ogrDataSource.GetLayer(i).GetLayerDefn().GetName())
            
            if 'PAR' not in _layerNames:
                self._raise_load_error(
                    'VFK file does not contain PAR layer.',
                    u'VFK soubor neobsahuje vrstvu parcel.',)
                QgsApplication.processEvents()
                return
            
            self.loadVfkFileProgressBar.setMaximum(_layerCount)
            
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
            in the 'puPlugin' Log Messages Panel, loadVfkLabel and Message Bar.
        
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
    
    def _load_vfk_layer(self, _vfkLayerCode, _filePath):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Args:
            _vfkLayerCode (str): The code of a layer.
            _filePath (str): A full path to the file.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'puPlugin' Log Messages Panel, loadVfkLabel and Message Bar.
        
        """
        
        _composedURI = _filePath + "|layername=" + _vfkLayerCode
        _layer = QgsVectorLayer(_composedURI, _vfkLayerCode, 'ogr')
        
        if _layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(_layer)
        else:
            self._raise_load_error(
                'Error loading layer', 'puPlugin',
                u'Chyba při načítání vrsty')
    
    def _raise_load_error(
            self, _engLogMsg, _czeLabelMsg, _czeBarMsg=None, _duration=5):
        """Displays error messages.
        
        Displays error messages in the 'puPlugin' Log Messages Panel,
        loadVfkLabel and Message Bar.
        
        Args:
            _engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            _czeLabelMsg (str): A message in the loadVfkLabel.
            _czeLabelMsg (str): A message in the Message Bar.
            _duration (int): A duration of the message in the Message Bar
                             in seconds.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'puPlugin' Log Messages Panel, loadVfkLabel and Message Bar.
        
        """
        
        _pluginName = 'puPlugin'
        
        if _czeBarMsg is None:
            _czeBarMsg = _czeLabelMsg
        
        QgsMessageLog.logMessage(_engLogMsg, _pluginName)
        self.loadVfkLabel.setText(_czeLabelMsg)
        iface.messageBar().pushMessage(
            _pluginName, _czeBarMsg , QgsMessageBar.WARNING, _duration)

