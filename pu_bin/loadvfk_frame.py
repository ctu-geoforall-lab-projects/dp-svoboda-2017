# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoadVfkFrame
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

from PyQt4.QtGui import (QFrame, QGridLayout, QLabel, QLineEdit, QPushButton,
                         QProgressBar, QFileDialog)
from PyQt4.QtCore import pyqtSignal, QFileInfo, QDir, QUuid, QSettings, QFile
from PyQt4.QtSql import QSqlDatabase, QSqlQuery

from qgis.gui import QgsMessageBar
from qgis.core import *

from osgeo import ogr

import traceback

from load_thread import LoadThread


class LoadVfkFrame(QFrame):
    """A frame which contains widgets for loading a VFK file."""
    
    text_browseVfkLineEdit = pyqtSignal(str)
    value_loadVfkProgressBar = pyqtSignal(int)
    
    def __init__(self, parentWidget, dockWidgetName, iface, dockWidget):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
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
        
        self.setObjectName(u'loadVfkFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.loadVfkGridLayout = QGridLayout(self)
        self.loadVfkGridLayout.setObjectName(u'loadVfkGridLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.browseVfkLabel = QLabel(self)
        self.browseVfkLabel.setObjectName(u'browseVfkLabel')
        self.browseVfkLabel.setText(u'VFK soubor:')
        self.loadVfkGridLayout.addWidget(self.browseVfkLabel, 0, 0, 1, 1)
        
        self.browseVfkLineEdit = QLineEdit(self)
        self.browseVfkLineEdit.setObjectName(u'browseVfkLineEdit')
        self.text_browseVfkLineEdit.connect(
            self._set_text_browseVfkLineEdit)
        self.browseVfkLineEdit.textChanged.connect(
            self.browseVfkLineEdit_textChanged)
        self.loadVfkGridLayout.addWidget(self.browseVfkLineEdit, 0, 1, 1, 1)
        
        self.browseVfkPushButton = QPushButton(self)
        self.browseVfkPushButton.setObjectName(u'browseVfkPushButton')
        self.browseVfkPushButton.clicked.connect(
            self.browseVfkPushButton_clicked)
        self.browseVfkPushButton.setText(u'Procházet')
        self.loadVfkGridLayout.addWidget(self.browseVfkPushButton, 0, 2, 1, 1)
        
        self.loadVfkProgressBar = QProgressBar(self)
        self.loadVfkProgressBar.setObjectName(u'loadVfkProgressBar')
        self.value_loadVfkProgressBar.connect(
            self._set_value_loadVfkProgressBar)
        self.value_loadVfkProgressBar.emit(0)
        self.loadVfkGridLayout.addWidget(self.loadVfkProgressBar, 1, 0, 1, 2)
        
        self.loadVfkPushButton = QPushButton(self)
        self.loadVfkPushButton.setObjectName(u'loadVfkPushButton')
        self.loadVfkPushButton.clicked.connect(self.loadVfkPushButton_clicked)
        self.loadVfkPushButton.setText(u'Načíst')
        self.loadVfkGridLayout.addWidget(self.loadVfkPushButton, 1, 2, 1, 1)
        self.loadVfkPushButton.setDisabled(True)
        
    def _set_text_browseVfkLineEdit(self, text):
        """Sets text.
        
        Args:
            text (str): A text to be written.
        
        """
        
        self.browseVfkLineEdit.setText(text)
    
    def _set_value_loadVfkProgressBar(self, value):
        """Sets a value to the progress bar.
        
        Args:
            text (str): A value to be set.
        
        """
        
        self.loadVfkProgressBar.setValue(value)
    
    def browseVfkPushButton_clicked(self):
        """Opens a file dialog and filters VFK files."""
        
        filePath = QFileDialog.getOpenFileName(
            self.dW, u'Načíst',
            self._last_used_path(),
            u'.vfk (*.vfk)')
        
        if not filePath:
            return
        
        self._set_last_used_path(filePath)
        
        self.text_browseVfkLineEdit.emit(filePath)
    
    def browseVfkLineEdit_textChanged(self):
        """Checks if the text in browseVfkLineEdit is a path to valid VFK file.
        
        If so, loadVfkPushButton is enabled, otherwise loadVfkPushButton
        is disabled.
        """
        
        tempText = self.browseVfkLineEdit.text()
        
        tempFileInfo = QFileInfo(tempText)
        
        if tempFileInfo.isFile() and tempFileInfo.suffix() in ('vfk', 'VFK'): 
            self.loadVfkPushButton.setEnabled(True)
        else:
            self.loadVfkPushButton.setEnabled(False)
    
    def loadVfkPushButton_clicked(self):
        """Starts loading the selected VFK file in a separate thread."""
        
        filePath = self.browseVfkLineEdit.text()
        
        self.dW.statusLabel.text_statusLabel.emit(
            u'Načítám data do SQLite databáze.')
        
        self._enable_load_widgets(False)
        
        QgsApplication.processEvents()
        
        self.loadThread = LoadThread(filePath)
        self.loadThread.work.connect(self.run_loading_vfk_layer)
        self.loadThread.start()
    
    def run_loading_vfk_layer(self, filePath):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        
        Args:
            filePath (str): A full path to the file.
        
        """
        
        self.value_loadVfkProgressBar.emit(0)
        
        fileInfo = QFileInfo(filePath)
        dbPath = QDir(
            fileInfo.absolutePath()).filePath(fileInfo.baseName() + '.db')
        vfkLayerCode = 'PAR'
        
        self._load_vfk_file(filePath, dbPath, vfkLayerCode)
        
        layerName = fileInfo.baseName() + '|' + vfkLayerCode
        
        self._load_vfk_layer(dbPath, vfkLayerCode, layerName)
        
        self._enable_load_widgets(True)
    
    def _load_vfk_file(self, filePath, dbPath, vfkLayerCode):
        """Loads a VFK file.
        
        Args:
            filePath (str): A full path to the file.
            dbPath (QDir): A full path to the database.
            vfkLayerCode (str): A code of the layer.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, statusLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            QgsApplication.registerOgrDrivers()
            QgsApplication.processEvents()
            
            dbInfo = QFileInfo(dbPath)
             
            if not dbInfo.isFile():
                vfkDriver = ogr.GetDriverByName('VFK')
                vfkDataSource = vfkDriver.Open(filePath)
                
                layer = vfkDataSource.GetLayerByName(vfkLayerCode)
                layer.GetFeatureCount()
                
                vfkDataSource.Destroy()
             
            self._open_database(dbPath)
             
            sqliteDriver = ogr.GetDriverByName('SQLite')
            sqliteDataSource = sqliteDriver.Open(str(dbPath))
            
            layerCount = sqliteDataSource.GetLayerCount()
            layerNames = []
            
            for i in xrange(layerCount):
                layerNames.append(
                    sqliteDataSource.GetLayer(i).GetLayerDefn().GetName())
            
            if 'PAR' not in layerNames:
                self._raise_load_error(
                    u'VFK file does not contain PAR layer, therefore it '
                    u'can not be loaded by PU Plugin. '
                    u'The file can be loaded by "Add Vector Layer"',
                    u'VFK soubor neobsahuje vrstvu parcel.',
                    u'VFK soubor neobsahuje vrstvu parcel, '
                    u'proto nemůže být pomocí PU Pluginu načten. '
                    u'Data je možné načíst pomocí "Přidat vektorovou vrstvu."')
                QgsApplication.processEvents()
                return
            
            self.loadVfkProgressBar.setRange(0, layerCount)
            
            for i in xrange(layerCount):
                self.value_loadVfkProgressBar.emit(i+1)
                self.dW.statusLabel.text_statusLabel.emit(
                    u'Načítám {} ({}/{})'
                    .format(layerNames[i], i+1, layerCount))
                
                QgsApplication.processEvents()
                
            self.dW.statusLabel.text_statusLabel.emit(
                u'Data byla úspešně načtena.')
        except:
            self._raise_load_error(
                u'Error loading VFK file.',
                u'Chyba při načítání VFK souboru.')
    
    def _open_database(self, dbPath):
        """Opens a database.
        
        Args:
            dbPath (QDir): A full path to the database.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, statusLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            if not QSqlDatabase.isDriverAvailable('QSQLITE'):
                self._raise_load_error(
                    u'SQLITE database driver is not available.',
                    u'Databázový ovladač QSQLITE není dostupný.')
                return
            
            connectionName = QUuid.createUuid().toString()
            QSqlDatabase.addDatabase("QSQLITE", connectionName)
            db = QSqlDatabase.database(connectionName)
            db.setDatabaseName(dbPath)
            db.open()
            
            self.setProperty('connectionName', connectionName)
            
            tableExistQuery = QSqlQuery(db)
            tableExistQuery.exec_(
                'select name'
                'from sqlite_master'
                'where type="table" and name in ("geometry_columns", "spatial_ref_sys")')
            
            if tableExistQuery.size() < 2:
                sqlFile = QFile(':/pu-vfk.sql', self)
                sqlFile.open(QFile.ReadOnly|QFile.Text)
            
                sqlQueries = sqlFile.readData(2000).split(';')
            
                query = QSqlQuery(db)
                for sqlQuery in sqlQueries:
                    query.exec_(sqlQuery)
            
            if not db.open():
                self._raise_load_error(
                    u'Database connection failed.',
                    u'Nepodařilo se připojit k databázi.')
        except:
            self._raise_load_error(
                u'Error opening database connection.',
                u'Chyba při otevírání databáze.')
    
    def _load_vfk_layer(self, dbPath, vfkLayerCode, layerName):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Also sets symbology according
        to "/plugins/puPlugin/data/qml/<vfkLayerCode>.qml" file and enables
        snapping.
        
        Args:
            dbPath (QDir): A full path to the database.
            vfkLayerCode (str): A code of the layer.
            layerName (str): A name of the layer.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, statusLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        try:
            composedURI = str(dbPath) + "|layername=" + vfkLayerCode
            layer = QgsVectorLayer(composedURI, layerName, 'ogr')
            
            if layer.isValid():
                style = ':/' + str(vfkLayerCode) + '.qml'
                layer.loadNamedStyle(style)
                QgsMapLayerRegistry.instance().addMapLayer(layer)
                
                QgsProject.instance().setSnapSettingsForLayer(
                    layer.id(), True, 2, 1, 10, True)
                self._set_options()
            else:
                self._raise_load_error(
                    u'Layer {} is not valid.'.format(vfkLayerCode),
                    u'Vrstva {} není platná.'.format(vfkLayerCode))
        except:
            self._raise_load_error(
                    u'Error loading {} layer.'.format(vfkLayerCode),
                    u'Chyba při načítání vrsty {}.'.format(vfkLayerCode))
    
    def _raise_load_error(
            self, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
        """Displays error messages.
    
        Displays error messages in the 'puPlugin' Log Messages Panel,
        statusLabel and Message Bar.
        
        For development purposes it displays traceback
        in the 'puPlugin Development' Log Messages Tab.
        
        Args:
            engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            czeLabelMsg (str): A message in the statusLabel.
            czeLabelMsg (str): A message in the Message Bar.
            duration (int): A duration of the message in the Message Bar
                             in seconds.
        
        Raises:
            The method handles exceptions by displaying error messages
            in the 'PU Plugin' Log Messages Tab, statusLabel, Message Bar
            and 'PU Plugin Development' Log Messages Tab.
        
        """
        
        pluginName = u'PU Plugin'
        
        if czeBarMsg is None:
            czeBarMsg = czeLabelMsg
        
        QgsMessageLog.logMessage(engLogMsg, pluginName)
        self.dW.statusLabel.text_statusLabel.emit(czeLabelMsg)
        self.iface.messageBar().pushMessage(
            pluginName, czeBarMsg , QgsMessageBar.WARNING, duration)
        
        developmentTb = u'PU Plugin Development'
        tb = traceback.format_exc()
        
        if 'None' not in tb:
            QgsMessageLog.logMessage(tb, developmentTb)
    
    def _enable_load_widgets(self, enableBool):
        """Sets enabled or disabled loading widgets.
        
        Sets enabled or disabled following widgets:
            browseVfkLineEdit
            browseVfkPushButton
            loadVfkPushButton
        
        Args:
            enableBool (bool): True to set enabled, False to set disabled.
        
        """
        
        self.browseVfkLineEdit.setEnabled(enableBool)
        self.browseVfkPushButton.setEnabled(enableBool)
        self.loadVfkPushButton.setEnabled(enableBool)
    
    def _last_used_path(self):
        """Gets last used path for file dialog.
                
        Returns:
            str: A last used path.
        
        """
        
        return QSettings().value('puplugin/lastVfkFilePath', '.')
    
    def _set_last_used_path(self, path):
        """Sets last used path for file dialog.
        
        Args:
            path (str): A path to be set.
        
        """
        
        QSettings().setValue('puplugin/lastVfkFilePath', path)
    
    def _set_options(self):
        """Sets topological editing enabled."""
        
        QgsProject.instance().setTopologicalEditing(True)

