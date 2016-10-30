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

from load_thread import LoadThread

from collections import namedtuple


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
        
        self.dW.statusLabel.text_statusLabel.emit(u'Načítám VFK soubor.')
        
        self._enable_load_widgets(False)
        
        filePath = self.browseVfkLineEdit.text()
        
        QgsApplication.processEvents()
        
        self.loadThread = LoadThread(filePath)
        self.loadThread.work.connect(self.run_loading_vfk_layer)
        self.loadThread.start()
    
    def run_loading_vfk_layer(self, filePath):
        """Calls methods for loading a VFK layer.
        
        Disables loading widgets until the loading is finished.
        
        Args:
            filePath (str): A full path to the file.
        
        Raises:
            dw.puError: When something goes wrong.
        
        """

        try:
            self.value_loadVfkProgressBar.emit(0)
            
            fileInfo = QFileInfo(filePath)
            dbPath = QDir(
                fileInfo.absolutePath()).filePath(fileInfo.baseName() + '.db')
            vfkLayerCode = 'PAR'
            
            self._load_vfk_file(filePath, dbPath, vfkLayerCode)
            
            puColumnsPAR = (
                'PU_KMENOVE_CISLO_PAR',
                'PU_PODDELENI_CISLA_PAR',
                'PU_VYMERA_PARCELY',
                'PU_KATEGORIE')
            
            self._open_database(dbPath, puColumnsPAR)
            
            layerName = fileInfo.baseName() + '|' + vfkLayerCode
            
            self._load_vfk_layer(dbPath, vfkLayerCode, layerName, puColumnsPAR)
            
            self.loadVfkProgressBar.setMaximum(1)
            self.value_loadVfkProgressBar.emit(1)
            
            self.dW.statusLabel.text_statusLabel.emit(
                u'Data byla úspešně načtena.')
        except self.dW.puError:
            pass
        except:
            self.dW._raise_pu_error(
                u'Error loading VFK file.',
                u'Chyba při načítání VFK souboru.')
        finally:
            self._enable_load_widgets(True)
    
    def _load_vfk_file(self, filePath, dbPath, vfkLayerCode):
        """Loads a VFK file.
        
        It checks if a database of the same name as VFK file exists.
        If not it creates it with VFK driver.
        
        Args:
            filePath (str): A full path to the file.
            dbPath (QDir): A full path to the database.
            vfkLayerCode (str): A code of the layer.
        
        """
        
        QgsApplication.registerOgrDrivers()
        QgsApplication.processEvents()
        
        dbInfo = QFileInfo(dbPath)

        if not dbInfo.isFile():
            self.dW.statusLabel.text_statusLabel.emit(
                u'Importuji data do SQLite databáze.')
            
            vfkDriver = ogr.GetDriverByName('VFK')
            vfkDataSource = vfkDriver.Open(filePath)
            
            vfkDdataSourceInfo = self._check_vfkLayerCode(
                vfkDataSource, vfkLayerCode)
            layerCount, layerNames = vfkDdataSourceInfo
            
            self.loadVfkProgressBar.setRange(0, layerCount)
            
            for i in xrange(layerCount):
                self.value_loadVfkProgressBar.emit(i+1)
                self.dW.statusLabel.text_statusLabel.emit(
                    u'Načítám {} ({}/{})'
                    .format(layerNames[i], i+1, layerCount))
                
                QgsApplication.processEvents()
            
            layer = vfkDataSource.GetLayerByName(vfkLayerCode)
            layer.GetFeatureCount()
            
            vfkDataSource.Destroy()
         
        sqliteDriver = ogr.GetDriverByName('SQLite')
        sqliteDataSource = sqliteDriver.Open(str(dbPath))
        
        sqliteDataSourceInfo = self._check_vfkLayerCode(
            sqliteDataSource, vfkLayerCode)
        layerCount, layerNames = sqliteDataSourceInfo
    
    def _check_vfkLayerCode(self, dataSource, vfkLayerCode):
        """Checks if there is a <vfkLayerCode> layer in the dataSource.
        
        Args:
            dataSource (osgeo.ogr.DataSource): A data source.
            vfkLayerCode (str): A code of the layer.
        
        Returns:
            int: A number of layers in the dataSource.
        
        Raises:
            dw.puError: When there is not <vfkLayerCode> layer
                in the dataSource.
        
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
                u'VFK file does not contain {} layer, therefore it can not be '
                u'loaded by PU Plugin. The file can be '
                u'loaded by "Add Vector Layer"'.format(vfkLayerCode),
                u'VFK soubor neobsahuje vrstvu {}.'.format(vfkLayerCode),
                u'VFK soubor neobsahuje vrstvu {}, proto nemůže být '
                u'pomocí PU Pluginu načten. Data je možné načíst '
                u'pomocí "Přidat vektorovou vrstvu."'.format(vfkLayerCode))
        
        DataSourceInfo = namedtuple(
            'DataSourceInfo', ['layerCount', 'layerNames'])
        
        dataSourceInfo = DataSourceInfo(layerCount, layerNames)
        
        return dataSourceInfo
    
    def _open_database(self, dbPath, puColumnsPAR):
        """Opens a database.
        
        Also checks if there are 'geometry_columns' and 'spatial_ref_sys'
        tables in the database, if not it creates and fills those tables.
        
        Args:
            dbPath (QDir): A full path to the database.
            puColumnsPAR (list): A list of columns that the plugin adds.
        
        Raises:
            dw.puError: When SQLITE database driver is not available
                or when database connection failed.
        
        """
        
        if not QSqlDatabase.isDriverAvailable('QSQLITE'):
            raise self.dW.puError(
                self.dW,
                u'SQLITE database driver is not available.',
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
                u'Nepodařilo se připojit k databázi.')
        
        self.setProperty('connectionName', connectionName)
        
        checkGcSrsFile = QFile(':/check_gc_srs.sql', self)
        checkGcSrsFile.open(QFile.ReadOnly|QFile.Text)
        
        query = checkGcSrsFile.readData(200)
        
        checkGcSrsQuery = QSqlQuery(db)
        checkGcSrsQuery.exec_(query)
        
        checkGcSrsSize = 0
        
        while checkGcSrsQuery.next():
            checkGcSrsSize += 1
        
        if checkGcSrsSize < 2:
            createFillGcSrsFile = QFile(':/create_fill_gc_srs.sql', self)
            createFillGcSrsFile.open(QFile.ReadOnly|QFile.Text)
        
            createFillGcSrsQueries = createFillGcSrsFile.readData(2000)\
                .split(';')
        
            createFillGcSrsQuery = QSqlQuery(db)
            
            for query in createFillGcSrsQueries:
                createFillGcSrsQuery.exec_(query)
        
        checkPuColumnsPARFile = QFile(':/check_pu_columns_PAR.sql', self)
        checkPuColumnsPARFile.open(QFile.ReadOnly|QFile.Text)
        
        query = checkPuColumnsPARFile.readData(50)
        
        checkPuColumnsPARQuery = QSqlQuery(db)
        checkPuColumnsPARQuery.exec_(query)
        
        columnsPAR = []

        while checkPuColumnsPARQuery.next():
            record = checkPuColumnsPARQuery.record()
            name = str(record.value('name'))
            columnsPAR.append(name)
        
        if not all(column in columnsPAR for column in puColumnsPAR):
            addPuColumnPARFile = QFile(':/add_pu_columns_PAR.sql', self)
            addPuColumnPARFile.open(QFile.ReadOnly|QFile.Text)
            
            addPuColumnsPARQueries = addPuColumnPARFile.readData(2000)\
                .split(';')
            
            addPuColumnPARQuery = QSqlQuery(db)
            
            for query in addPuColumnsPARQueries:
                addPuColumnPARQuery.exec_(query)
    
    def _load_vfk_layer(self, dbPath, vfkLayerCode, layerName, puColumnsPAR):
        """Loads a layer of the given code from VFK file into the map canvas.
        
        Also sets symbology according
        to "/plugins/puPlugin/data/qml/<vfkLayerCode>.qml" file, enables
        snapping and sets all fields except for those listed in puColumnsPAR
        non-editable.
        
        Args:
            dbPath (QDir): A full path to the database.
            vfkLayerCode (str): A code of the layer.
            layerName (str): A name of the layer.
            puColumnsPAR (list): A list of columns that the plugin adds.
        
        Raises:
            dw.puError: When <vfkLayerCode> layer is not valid.
        
        """
        
        blacklistedDriver = ogr.GetDriverByName('VFK')
        blacklistedDriver.Deregister()
        
        composedURI = str(dbPath) + "|layername=" + vfkLayerCode
        layer = QgsVectorLayer(composedURI, layerName, 'ogr')
        
        blacklistedDriver.Register()
        
        fields = layer.pendingFields()
        fieldNames = [field.name() for field in fields]
        
        formConfig = layer.editFormConfig()
        
        for i in layer.pendingAllAttributesList():
            if fields[i].name() not in puColumnsPAR:
                formConfig.setReadOnly(i)
        
        if layer.isValid():
            style = ':/' + str(vfkLayerCode) + '.qml'
            layer.loadNamedStyle(style)
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            
            QgsProject.instance().setSnapSettingsForLayer(
                layer.id(), True, 2, 1, 10, True)
            self._set_options()
        else:
            raise self.dW.puError(
                self.dW,
                u'Layer {} is not valid.'.format(vfkLayerCode),
                u'Vrstva {} není platná.'.format(vfkLayerCode))
    
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

