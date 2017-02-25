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
from PyQt4.QtCore import pyqtSignal, QFileInfo, QDir, QUuid, QFile, Qt
from PyQt4.QtSql import QSqlDatabase, QSqlQuery

from qgis.core import *

from osgeo import ogr

from load_thread import LoadThread


class LoadVfkFrame(QFrame):
    """A frame which contains widgets for loading a VFK file."""
    
    set_text_statusbar = pyqtSignal(str, int)
    text_browseVfkLineEdit = pyqtSignal(str)
    value_loadVfkProgressBar = pyqtSignal(int)
    
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
        
        super(LoadVfkFrame, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'loadVfkFrame')
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        self.set_text_statusbar.connect(self.dW.statusBar.set_text_statusbar)
        self.set_text_statusbar.emit(u'Vyberte VFK soubor.', 0)
        
        self.loadVfkGridLayout = QGridLayout(self)
        self.loadVfkGridLayout.setObjectName(u'loadVfkGridLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.browseVfkLabel = QLabel(self)
        self.browseVfkLabel.setObjectName(u'browseVfkLabel')
        self.browseVfkLabel.setFixedHeight(self.browseVfkLabel.height())
        self.browseVfkLabel.setText(u'VFK soubor:')
        self.loadVfkGridLayout.addWidget(self.browseVfkLabel, 0, 0, 1, 1)
        
        self.browseVfkLineEdit = QLineEdit(self)
        self.browseVfkLineEdit.setObjectName(u'browseVfkLineEdit')
        self.browseVfkLineEdit.setFixedHeight(self.browseVfkLineEdit.height())
        self.text_browseVfkLineEdit.connect(self._set_text_browseVfkLineEdit)
        self.browseVfkLineEdit.textChanged.connect(
            self._check_vfk_file_path)
        self.loadVfkGridLayout.addWidget(self.browseVfkLineEdit, 0, 1, 1, 1)
        
        self.browseVfkPushButton = QPushButton(self)
        self.browseVfkPushButton.setObjectName(u'browseVfkPushButton')
        self.browseVfkPushButton.setFixedHeight(
            self.browseVfkPushButton.height())
        self.browseVfkPushButton.clicked.connect(
            self._browse_vfk_files)
        self.browseVfkPushButton.setText(u'Procházet')
        self.loadVfkGridLayout.addWidget(self.browseVfkPushButton, 0, 2, 1, 1)
        
        self.loadVfkGridLayout.setRowStretch(1, 1)
        
        self.loadVfkProgressBar = QProgressBar(self)
        self.loadVfkProgressBar.setObjectName(u'loadVfkProgressBar')
        self.loadVfkProgressBar.setFixedHeight(
            self.loadVfkProgressBar.height())
        self.loadVfkProgressBar.setMinimum(0)
        self.value_loadVfkProgressBar.connect(
            self._set_value_loadVfkProgressBar)
        self.value_loadVfkProgressBar.emit(0)
        self.loadVfkGridLayout.addWidget(self.loadVfkProgressBar, 2, 0, 1, 2)
        
        self.loadVfkPushButton = QPushButton(self)
        self.loadVfkPushButton.setObjectName(u'loadVfkPushButton')
        self.loadVfkPushButton.setFixedHeight(self.loadVfkPushButton.height())
        self.loadVfkPushButton.clicked.connect(self._start_loading_vfk_layer)
        self.loadVfkPushButton.setText(u'Načíst')
        self.loadVfkGridLayout.addWidget(self.loadVfkPushButton, 2, 2, 1, 1)
        self.loadVfkPushButton.setDisabled(True)
    
    def _set_text_browseVfkLineEdit(self, text):
        """Sets text to the browseVfkLineEdit.
        
        Args:
            text (str): A text to be set.
        
        """
        
        self.browseVfkLineEdit.setText(text)
    
    def _set_value_loadVfkProgressBar(self, value):
        """Sets value to the loadVfkProgressBar.
        
        Args:
            text (str): A value to be set.
        
        """
        
        self.loadVfkProgressBar.setValue(value)
    
    def _browse_vfk_files(self):
        """Opens a file dialog and filters VFK files."""
        
        title = u'Vyberte VFK soubor.'
        filters = u'.vfk (*.vfk)'
        
        filePath = self.dW.open_file_dialog(title, filters, True)
        
        if filePath:
            self.text_browseVfkLineEdit.emit(filePath)
    
    def _check_vfk_file_path(self):
        """Checks if text in the browseVfkLineEdit is a path to a VFK file.
        
        If so, the loadVfkPushButton is enabled,
        otherwise the loadVfkPushButton is disabled.
        
        """
        
        tempText = self.browseVfkLineEdit.text()
        
        tempFileInfo = QFileInfo(tempText)
        
        if tempFileInfo.isFile() and tempFileInfo.suffix() in (u'vfk', u'VFK'): 
            self.loadVfkPushButton.setEnabled(True)
        else:
            self.loadVfkPushButton.setEnabled(False)
    
    def _start_loading_vfk_layer(self):
        """Starts loading the selected VFK file in a separate thread."""
        
        self.set_text_statusbar.emit(
            u'Načítám VFK soubor. Tento proces může chvíli trvat...', 0)
        
        self._enable_load_widgets(False)
        
        filePath = self.browseVfkLineEdit.text()
        
        QgsApplication.processEvents()
        
        self.loadThread = LoadThread(filePath)
        self.loadThread.work.connect(self._run_loading_vfk_layer)
        self.loadThread.start()
    
    def _run_loading_vfk_layer(self, filePath):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        
        Args:
            filePath (str): A full path to the file.
        
        """

        try:
            self.value_loadVfkProgressBar.emit(0)
            
            fileInfo = QFileInfo(filePath)
            dbPath = QDir(fileInfo.absolutePath())\
                .filePath(fileInfo.completeBaseName() + '.db')
            vfkLayerCode = 'PAR'
            vfkDriverName = 'VFK'
            layerName = fileInfo.completeBaseName() + '|' + vfkLayerCode
            
            self._create_db_file(filePath, dbPath, vfkLayerCode, vfkDriverName)
            
            self._open_database(dbPath)
            
            self._load_vfk_layer(dbPath, layerName, vfkLayerCode, vfkDriverName)
            
            self.loadVfkProgressBar.setMaximum(1)
            self.value_loadVfkProgressBar.emit(1)
            
            self.set_text_statusbar.emit(u'Data byla úspešně načtena.', 0)
        except self.dW.puError:
            QgsApplication.processEvents()
        except:
            QgsApplication.processEvents()
            
            self.dW.display_error_messages(
                u'Error loading VFK file "{}".'.format(filePath),
                u'Chyba při načítání VFK souboru.',
                u'Chyba při načítání VFK souboru "{}".'.format(filePath))
        finally:
            QgsApplication.processEvents()
            self._enable_load_widgets(True)
    
    def _create_db_file(self, filePath, dbPath, vfkLayerCode, vfkDriverName):
        """Creates a database file.
        
        It checks if a database of the same name as the file exists.
        If not it creates the database with a VFK driver.
        
        Args:
            filePath (str): A full path to the file.
            dbPath (str): A full path to the database.
            vfkLayerCode (str): A code of the layer.
            vfkDriverName (str): A name of the VFK driver.
        
        Raises:
            dw.puError: When the VFK driver failed to open VFK file
                or when the SQlite driver failed to open the database.
        
        """
        
        QgsApplication.processEvents()
        
        dbInfo = QFileInfo(dbPath)

        if not dbInfo.isFile():
            self.set_text_statusbar.emit(
                u'Importuji data do SQLite databáze...', 0)
            
            QgsApplication.registerOgrDrivers()
            
            vfkDriver = ogr.GetDriverByName(vfkDriverName)
            vfkDataSource = vfkDriver.Open(filePath)
            
            QgsApplication.processEvents()
            
            if not vfkDataSource:
                raise self.dW.puError(
                    self.dW,
                    u'Failed to load data, "{}" is not a valid VFK datasource.'
                    .format(dbPath),
                    u'Data nelze načíst.',
                    u'Data nelze načíst, "{}" není platný datový zdroj VFK.'
                    .format(dbPath))
            
            layerCount, layerNames = self._check_vfkLayerCode(
                vfkDataSource, vfkLayerCode)
            
            self.loadVfkProgressBar.setMaximum(layerCount)
            
            for i in xrange(layerCount):
                self.value_loadVfkProgressBar.emit(i+1)
                self.set_text_statusbar.emit(
                    u'Načítám vrstvu {} ({}/{})...'
                    .format(layerNames[i], i+1, layerCount), 0)
            
            QgsApplication.processEvents()
            
            self._build_geometry(vfkLayerCode, vfkDataSource)
            
            QgsApplication.processEvents()
            
            vfkDataSource.Destroy()
        
        sqliteDriver = ogr.GetDriverByName('SQLite')
        sqliteDataSource = sqliteDriver.Open(dbPath)
        
        if not sqliteDataSource:
            raise self.dW.puError(
                self.dW,
                u'Failed to load data, "{}" is not a valid SQLite datasource.'
                .format(dbPath),
                u'Data nelze načíst.',
                u'Data nelze načíst, "{}" není platný datový zdroj SQLite.'
                .format(dbPath))

        layerCount, layerNames = self._check_vfkLayerCode(
            sqliteDataSource, vfkLayerCode)
        
        sqliteDataSource.Destroy()
    
    def _check_vfkLayerCode(self, dataSource, vfkLayerCode):
        """Checks if there is a vfkLayerCode layer in the dataSource.
        
        Args:
            dataSource (osgeo.ogr.DataSource): A data source.
            vfkLayerCode (str): A code of the layer.
        
        Returns:
            tuple:
                [0] (int): A number of layers in the dataSource.
                [1] (list): A list of layer names in the dataSource.
        
        Raises:
            dw.puError: When there is no vfkLayerCode layer in the dataSource.
        
        """
        
        layerCount = dataSource.GetLayerCount()
        
        layerNames = []
        
        for i in xrange(layerCount):
            layerNames.append(dataSource.GetLayer(i).GetLayerDefn().GetName())
        
        if vfkLayerCode not in layerNames:
            QgsApplication.processEvents()
            
            dataSource.Destroy()
            
            raise self.dW.puError(
                self.dW,
                u'VFK file does not contain "{}" layer, therefore it can not be '
                u'loaded by PU Plugin. The file can be '
                u'loaded by "Add Vector Layer"'.format(vfkLayerCode),
                u'VFK soubor neobsahuje vrstvu {}.'.format(vfkLayerCode),
                u'VFK soubor neobsahuje vrstvu {}, proto nemůže být '
                u'pomocí PU Pluginu načten. Data je možné načíst '
                u'pomocí "Přidat vektorovou vrstvu."'.format(vfkLayerCode))
        
        dataSourceInfo = (layerCount, layerNames)
        
        return dataSourceInfo
    
    def _build_geometry(self, layerCode, dataSource):
        """Builds a geometry for the layer in the data source..
        
        Args:
            layerCode (str): A code of the layer.
            dataSource (ogr.DataSource) A reference to the OGR data source.
        
        """
        
        codeLayer = dataSource.GetLayerByName(layerCode)
        
        codeLayer.GetFeatureCount(True)
        
        for feature in codeLayer:
            feature.GetGeometryRef()
    
    def _open_database(self, dbPath):
        """Opens a database.
        
        Checks if there are geometry_columns and spatial_ref_sys
        tables in the database, if not it creates and fills those tables.
        
        Checks f there are all PU columns in PAR table,
        if it it creates and fills those columns.
        
        Args:
            dbPath (str): A full path to the database.
        
        Raises:
            dw.puError: When SQLITE database driver is not available
                or when database connection failes.
        
        """
        
        if not QSqlDatabase.isDriverAvailable('QSQLITE'):
            raise self.dW.puError(
                self.dW,
                u'SQLITE database driver is not available.',
                u'Databázový ovladač QSQLITE není dostupný.',
                u'Databázový ovladač QSQLITE není dostupný.')
        
        connectionName = QUuid.createUuid().toString()
        QSqlDatabase.addDatabase("QSQLITE", connectionName)
        db = QSqlDatabase.database(connectionName)
        db.setDatabaseName(dbPath)
        db.open()
        
        if not db.open():
            raise self.dW.puError(
                self.dW,
                u'Database connection failed.',
                u'Nepodařilo se připojit k databázi.',
                u'Nepodařilo se připojit k databázi.')
        
        sqlQuery = QSqlQuery(db)
        
        sqlDir = QDir(self.dW.pluginDir + u'/data/sql')
        
        query = self._read_text_from_file(sqlDir.filePath(u'check_gc_srs.sql'))
        
        sqlQuery.exec_(query)
        
        QgsApplication.processEvents()
        
        checkGcSrsSize = 0
        
        while sqlQuery.next():
            checkGcSrsSize += 1
        
        if checkGcSrsSize < 2:
            queries = self._read_text_from_file(
                sqlDir.filePath(u'create_fill_gc_srs.sql')).split(';')
            
            for query in queries:
                sqlQuery.exec_(query)
                
                QgsApplication.processEvents()
        
        query = self._read_text_from_file(
            sqlDir.filePath(u'check_pu_columns_PAR.sql'))
        
        sqlQuery.exec_(query)
        
        QgsApplication.processEvents()
        
        columnsPAR = []

        while sqlQuery.next():
            record = sqlQuery.record()
            name = str(record.value('name'))
            columnsPAR.append(name)
        
        if not all(column in columnsPAR for column in self.dW.allPuColumnsPAR):
            queries = self._read_text_from_file(
                sqlDir.filePath(u'add_pu_columns_PAR.sql')).split(';')
            
            for query in queries:
                sqlQuery.exec_(query)
                
                QgsApplication.processEvents()
    
    def _read_text_from_file(self, filePath, maxSize=2000):
        """Reads text from the given file.
        
        Args:
            filePath (str): A full path to the file.
            maxSize (int): Maximum size of read data from the file in bytes.
        
        Returns:
            str: The text from the file.
        
        """
        
        file = QFile(filePath)
        file.open(QFile.ReadOnly|QFile.Text)
        
        text = file.readData(maxSize)
        
        file.close()
        
        return text
    
    def _load_vfk_layer(self, dbPath, layerName, vfkLayerCode, vfkDriverName):
        """Loads a layer of the given code from database into the map canvas.
        
        Also sets symbology according
        to "../puplugin/data/qml/vfkLayerCode.qml" file, enables
        snapping, sets all fields except for those listed
        in dW.editablePuColumnsPAR non-editable and hides all fields
        except for those listed in dW.allVisibleColumnsPAR.
        
        Args:
            dbPath (str): A full path to the database.
            layerName (str): A name of the layer.
            vfkLayerCode (str): A code of the layer.
            vfkDriverName (str): A name of the VFK driver.
        
        Raises:
            dw.puError: When vfkLayerCode layer is not valid.
        
        """
        
        self.set_text_statusbar.emit(
            u'Přidávám vrstvu {}...'.format(vfkLayerCode), 0)
        
        blacklistedDriver = ogr.GetDriverByName(vfkDriverName)
        blacklistedDriver.Deregister()
        
        composedURI = dbPath + '|layername=' + vfkLayerCode
        layer = QgsVectorLayer(composedURI, layerName, 'ogr')
        
        blacklistedDriver.Register()
        
        fields = layer.pendingFields()
        
        formConfig = layer.editFormConfig()
        
        for i in layer.pendingAllAttributesList():
            if fields[i].name() not in self.dW.editablePuColumnsPAR:
                formConfig.setReadOnly(i)
                formConfig.setWidgetType(i, 'Hidden')
        
        if layer.isValid():
            style = ':/' + vfkLayerCode + '.qml'
            layer.loadNamedStyle(style)
            
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            
            QgsApplication.processEvents()
            
            self._set_layer_snapping(layer)
            
            fields = layer.pendingFields()
            
            tableConfig = layer.attributeTableConfig()
            tableConfig.update(fields)
            
            columns = tableConfig.columns()
            
            for column in columns:
                if column.name not in self.dW.allVisibleColumnsPAR:
                    column.hidden = True
            
            tableConfig.setColumns(columns)
            layer.setAttributeTableConfig(tableConfig)
            
            QgsApplication.processEvents()
        else:
            raise self.dW.puError(
                self.dW,
                u'Layer {} is not valid.'.format(vfkLayerCode),
                u'Vrstva {} není platná.'.format(vfkLayerCode),
                u'Vrstva {} není platná.'.format(vfkLayerCode))
    
    def _set_layer_snapping(self, layer):
        """Sets layer snapping.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        """
        
        project = QgsProject.instance()
        project.setTopologicalEditing(True)
        project.writeEntry('Digitizing', 'SnappingMode', 'advanced') 
        project.writeEntry('Digitizing', 'IntersectionSnapping', Qt.Checked)
        project.setSnapSettingsForLayer(layer.id(), True, 2, 1, 10, False)
    
    def _enable_load_widgets(self, enableBool):
        """Sets loading widgets enabled or disabled.
        
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

