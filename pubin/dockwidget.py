# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DockWidget
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

from PyQt4.QtGui import (QDockWidget, QWidget, QSizePolicy, QGridLayout,
                         QFrame, QFileDialog)
from PyQt4.QtCore import pyqtSignal, QDir, QSettings, QFileInfo

from qgis.gui import QgsMessageBar
from qgis.core import *

import traceback
import sys

from statusbar import StatusBar
from toolbar import ToolBar
from stackedwidget import StackedWidget


class DockWidget(QDockWidget):
    """A main widget of the plugin."""
    
    def __init__(self, iface, pluginDir, name):
        """Constructor.
        
        Args:
            iface (QgisInterface): A reference to the QgisInterface.
            pluginDir (str): A plugin directory.
            name (str): A name of the plugin.
        
        """
        
        self.iface = iface
        self.pluginDir = QDir(pluginDir)
        self.name = name
        
        super(DockWidget, self).__init__()
        
        self._setup_self()
       
    def _setup_self(self):
        """Sets up self."""
        
        self.editablePuColumnsPAR = (
            'PU_KMENOVE_CISLO_PAR',
            'PU_PODDELENI_CISLA_PAR')
        
        self.visiblePuColumnsPAR = \
            self.editablePuColumnsPAR + \
            ('PU_VYMERA_PARCELY', 'PU_VZDALENOST', 'PU_CENA')
        
        self.allPuColumnsPAR = \
            self.visiblePuColumnsPAR + ('PU_KATEGORIE', 'PU_ID')
        
        self.visibleDefaultColumnsPAR = (
            'KMENOVE_CISLO_PAR',
            'PODDELENI_CISLA_PAR',
            'VYMERA_PARCELY')
        
        self.allVisibleColumnsPAR = \
            self.visiblePuColumnsPAR + self.visibleDefaultColumnsPAR
        
        self.uniqueDefaultColumnsPAR = ('rowid', 'ID', 'ogr_fid')
        
        self.allDefaultColumnsPAR = \
            self.visibleDefaultColumnsPAR + self.uniqueDefaultColumnsPAR
        
        self.requiredColumnsPAR = \
            self.allPuColumnsPAR + self.allDefaultColumnsPAR
        
        self.vertexVfkLayerCodes = ('SOBR', 'SPOL', 'HEY')
        
        self.dWName = u'dockWidget'
        
        self.settings = QSettings(self)
        
        self.setObjectName(self.dWName)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.widget = QWidget(self)
        self.widget.setObjectName(u'widget')
        self.setWidget(self.widget)
        
        self.gridLayout = QGridLayout(self.widget)
        self.gridLayout.setObjectName(u'gridLayout')
        
        self.setWindowTitle(self.name)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.lastActiveLayer = None
        self._disconnect_connect_ensure_unique_field_values()
        self.iface.currentLayerChanged.connect(
            self._disconnect_connect_ensure_unique_field_values)
        
        self.toolBar = ToolBar(self, self.dWName, self.iface, self.pluginDir)
        self.gridLayout.addWidget(self.toolBar, 0, 0, 1, 1)
        
        self.statusBar = StatusBar(
            self, self.dWName, self.iface, self.pluginDir)
        self.gridLayout.addWidget(self.statusBar, 2, 0, 1, 1)
        
        self.frame = QFrame(self)
        self.frame.setObjectName(u'frame')
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout.addWidget(self.frame, 1, 0, 1, 1)
        
        self.stackedWidget = StackedWidget(
            self, self.dWName, self.iface, self.pluginDir)
        self.gridLayout.addWidget(self.stackedWidget, 1, 0, 1, 1)
    
    def display_error_messages(
            self,
            sender,
            engLogMessage, czeStatusBarMessage=None, czeMessageBarMessage=None,
            duration=20):
        """Displays error messages.
        
        Displays error messages in the Log Messages Tab, the statusBar
        and the Message Bar.
        
        Args:
            sender (QWidget): A reference to the sender widget.
            engLogMessage (str): A message in the 'PU Plugin' Log Messages Tab.
            czeStatusBarMessage (str): A message in the statusBar.
            czeMessageBarMessage (str): A message in the Message Bar.
            duration (int): A duration of the message in the Message Bar
                in seconds.
        
        """
        
        sender.set_text_statusbar.emit(u'', 1)
        
        pluginName = u'PU Plugin'
        
        type, value, mytraceback = sys.exc_info()
        
        if type:
            tb = traceback.format_exc()
            engLogMessage = engLogMessage + '\n' + tb
        
        QgsMessageLog.logMessage(engLogMessage, pluginName)
        
        if czeStatusBarMessage:
            sender.set_text_statusbar.emit(czeStatusBarMessage, duration)
        
        if czeMessageBarMessage:
            self.iface.messageBar().pushMessage(
                pluginName, czeMessageBarMessage ,
                QgsMessageBar.WARNING, duration)
    
    class puError(Exception):
        """A custom exception."""
        
        def __init__(
                self,
                dW, sender,
                engLogMessage,
                czeStatusBarMessage=None,
                czeMessageBarMessage=None,
                duration=20):
            """Constructor.
            
            Args:
                dW (QWidget): A reference to the dock widget.
                sender (QWidget): A reference to the sender widget.
                engLogMessage (str): A message in the 'PU Plugin' Log Messages
                    Tab.
                czeStatusBarMessage (str): A message in the statusBar.
                czeMessageBarMessage (str): A message in the Message Bar.
                duration (int): A duration of the message in the Message Bar
                    in seconds.
                
            """
            
            super(Exception, self).__init__(dW)
            
            dW.display_error_messages(
                sender,
                engLogMessage, czeStatusBarMessage, czeMessageBarMessage,
                duration)
    
    def _get_settings(self, key):
        """Returns a value for the settings key.
        
        Args:
            key (str): A settings key.
                
        Returns:
            str: A value for the settings key.
        
        """
        
        value = self.settings.value(key, '')
        
        return value
    
    def _set_settings(self, key, value):
        """Sets the value for the settings key.
        
        Args:
            key (str): A settings key.
            value (str): A value to be set.
        
        """
        
        self.settings.setValue(key, value)
    
    def open_file_dialog(self, title, filters, existence):
        """Opens a file dialog.
        
        Args:
            title (str): A title of the file dialog.
            filters (str): Available filter(s) of the file dialog.
            existence (bool):
                True when the file has to exist
                (QFileDialog.getOpenFileNameAndFilter).
                False when the file does not have to exist
                (QFileDialog.getSaveFileNameAndFilter).
        
        Returns:
            str: A path to the selected file.
        
        """
        
        sender = self.sender().objectName()
        
        lastUsedFilePath = self._get_settings(sender + '-' + 'lastUsedFilePath')
        lastUsedFilter = self._get_settings(sender + '-' + 'lastUsedFilter')
        
        if existence:
            filePath, usedFilter = QFileDialog.getOpenFileNameAndFilter(
                self, title, lastUsedFilePath, filters, lastUsedFilter)
        else:
            filePath, usedFilter = QFileDialog.getSaveFileNameAndFilter(
                self, title, lastUsedFilePath, filters, lastUsedFilter,
                QFileDialog.DontConfirmOverwrite)
        
        if filePath and usedFilter:
            self._set_settings(sender + '-' + 'lastUsedFilePath', filePath)
            self._set_settings(sender + '-' + 'lastUsedFilter', usedFilter)
        
        return filePath
    
    def set_field_value_for_features(
            self, layer, features, field, value, startCommit=True):
        """Sets the field value for the given features.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            features (QgsFeatureIterator): A feature iterator.
            field (str): A name of the field.
            value (int): A value to be set.
            startCommit (bool): True for start editing and commit changes,
                False otherwise.
        
        """
        
        fieldID = layer.fieldNameIndex(field)
        
        if startCommit:
            layer.startEditing()
        
        layer.updateFields()
        
        for feature in features:
            if feature.attribute(field) != value:
                featureID = feature.id()
                layer.changeAttributeValue(featureID, fieldID, value)
        
        if startCommit:
            layer.commitChanges()
        
        QgsApplication.processEvents()
    
    def check_layer(self, sender=None, layer=False):
        """Checks the active or the given layer.
        
        If layer is False, the active layer is taken.
        
        First it checks if there is a layer, then if the layer is valid,
        then if the layer is vector and finally if the active layer contains
        all required columns.
        
        Emitted messages are for checking the active layer.
        In other words, when sender is not None, layer should be False,
        otherwise emitted messages will not make sense.
        
        Args:
            sender (object): A reference to the sender object. 
            layer (QgsVectorLayer): A reference to the layer.
        
        Returns:
            tuple:
                [0] (bool): True when there is a vector layer that contains
                    all required columns, False otherwise.
                [1] (QgsVectorLayer): A reference to the layer.
        
        """
        
        if layer == False:
            layer = self.iface.activeLayer()
        
        duration = 10
        
        if not layer:
            if sender:
                sender.set_text_statusbar.emit(
                    u'Žádná aktivní vrstva.', duration)
            successLayer = (False, layer)
            return successLayer
        
        if not layer.isValid():
            if sender:
                sender.set_text_statusbar.emit(
                    u'Aktivní vrstva není platná.', duration)
            successLayer = (False, layer)
            return successLayer
        
        if not layer.type() == 0:
            if sender:
                sender.set_text_statusbar.emit(
                    u'Aktivní vrstva není vektorová.', duration)
            successLayer = (False, layer)
            return successLayer
        
        fieldNames = [field.name().upper() for field in layer.pendingFields()]
        
        if not all(column.upper() in fieldNames for column in self.requiredColumnsPAR):
            if sender:
                sender.set_text_statusbar.emit(
                    u'Aktivní vrstva není VFK.', duration)
            successLayer = (False, layer)
            return successLayer
        
        successLayer = (True, layer)
        return successLayer
    
    def check_perimeter_layer(self, perimeterLayer, layer, message=None):
        """Checks the perimeter layer.
        
        Checks if the perimeter layer contains all required columns,
        if the suffix is 'pu.shp' and if the perimeter layer has same CRS
        as the given layer.
        
        Args:
            perimeterLayer (QgsVectorLayer): A reference to the perimeter layer.
            layer (QgsVectorLayer): A reference to the layer.
        
        Returns:
            bool: True when the perimeter layer contains all required columns
                and the suffix is 'pu.shp', False otherwise.
        
        """
        
        duration = 10
        
        if not perimeterLayer:
            if message:
                self.set_text_statusbar.emit(u'Žádná vrstva obvodu.', duration)
            return False
        
        perimeterFieldNames = \
            [field.name() for field in perimeterLayer.pendingFields()]
        
        if not all(column[:10] in perimeterFieldNames \
                   for column in self.requiredColumnsPAR):
            if message:
                self.set_text_statusbar.emit(
                    u'Vrstva obvodu nebyla vytvořena PU Pluginem.', duration)
            return False
        
        perimeterFileInfo = QFileInfo(perimeterLayer.source())
        
        if u'pu.shp' not in perimeterFileInfo.completeSuffix():
            if message:
                self.set_text_statusbar.emit(
                    u'Vrstva obvodu není obvod vytvořený PU Pluginem.',
                    duration)
            return False
        
        perimeterLayerCrs = perimeterLayer.crs().authid()
        layerCrs = layer.crs().authid()
        
        if perimeterLayerCrs != layerCrs:
            if message:
                self.set_text_statusbar.emit(
                    u'Aktivní vrstva a vrstva obvodu nemají stejný '
                    u'souřadnicový systém.', duration)
            return False
        
        return True
    
    def check_loaded_layers(self, filePath):
        """Checks if the given layer is already loaded.
        
        Args:
            filePath (str): A full path of the file to be checked.
        
        Returns:
            QgsVectorLayer: A reference to the layer with the same source as
                the given path, None when there is not such a layer.
        
        """
        
        layers = self.iface.legendInterface().layers()
        
        loadedLayer = None
        
        for layer in layers:
            if filePath == layer.source():
                loadedLayer = layer
                break
        
        return loadedLayer
    
    def check_editing(self):
        """Checks if editing is enabled.
        
        Returns:
            bool: True when editing is enabled, False otherwise.
        
        """
        
        if self.stackedWidget.editPuWidget.toggleEditingAction.isChecked():
            return True
        else:
            return False
    
    def select_features_by_field_value(self, layer, field, value):
        """Selects features in the given layer by the field value.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            field (str): A name of the field.
            value (str) A value of the field.
        
        """
        
        expression = QgsExpression("\"{}\" = {}".format(field, value))
        
        features = layer.getFeatures(QgsFeatureRequest(expression))
        
        featuresID = [feature.id() for feature in features]
        
        layer.selectByIds(featuresID)
    
    def select_features_by_expression(self, layer, expression):
        """Selects features in the given layer by the expression.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            expression (QgsExpression): An expression.
        
        """
        
        features = layer.getFeatures(QgsFeatureRequest(expression))
        
        featuresID = [feature.id() for feature in features]
        
        layer.selectByIds(featuresID)
    
    def delete_features_by_expression(
            self, layer, expression, startCommit=True):
        """Deletes features from the given layer by the expression.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            expression (QgsExpression): An expression.
            startCommit (bool): True for start editing and commit changes,
                False otherwise.
        
        """
        
        features = layer.getFeatures(QgsFeatureRequest(expression))
        
        featuresID = [feature.id() for feature in features]
        
        if startCommit:
            layer.startEditing()
        
        layer.deleteFeatures(featuresID)
        
        if startCommit:
            layer.commitChanges()
    
    def disconnect_from_iface(self):
        """Disconnects functions from the QgsInterface."""
        
        self._disconnect_connect_ensure_unique_field_values(False)
        
        self.iface.currentLayerChanged.disconnect(
            self._disconnect_connect_ensure_unique_field_values)
        
        QgsApplication.processEvents()
        
    def _disconnect_connect_ensure_unique_field_values(self, connection=True):
        """Disconnects (and connects) function for ensuring unique field values.
        
        First it checks if lastActiveLayer was created by PU Plugin.
        If so, it disconnects function that ensures unique field values
        from beforeCommitChanges signal.
        Then it checks if the active layer was created by PU Plugin.
        If connection is True it connects function that ensures unique field
        values to beforeCommitChanges signal.
        
        Args:
            connection (bool):
                True for connecting function that ensures unique field values
                to beforeCommitChanges signal, False for not connecting.
        
        """
        
        try:
            succes, layer = self.check_layer(None, self.lastActiveLayer)
            
            if succes:
                layer.beforeCommitChanges.disconnect(
                    self._ensure_unique_field_values)
            
            succes, self.lastActiveLayer = self.check_layer(None)
            
            if succes and connection:
                self.lastActiveLayer.beforeCommitChanges.connect(
                    self._ensure_unique_field_values)
        except:
            self.display_error_messages(
                self,
                u'Error connecting/disconnecting '
                u'_ensure_unique_field_values function.')
    
    def _ensure_unique_field_values(self):
        """Ensures that field values are unique.
        
        Sets following fields to None for new features:
            rowid
            ID
            ogr_fid
        
        """
        
        try:
            layer = self.iface.activeLayer()
            
            selectedFeaturesIDs = layer.selectedFeaturesIds()
                
            features = layer.getFeatures()
            
            rowidColumn = self.uniqueDefaultColumnsPAR[0]
            idColumn = self.uniqueDefaultColumnsPAR[1]
            ogrfidColumn = self.uniqueDefaultColumnsPAR[2]
            
            rowidGroupedFeatures = {}
            
            for feature in features:
                featureRowid = feature.attribute(rowidColumn)
                
                if featureRowid not in rowidGroupedFeatures:
                    rowidGroupedFeatures[featureRowid] = 1
                else:
                    rowidGroupedFeatures[featureRowid] += 1
            
            rowidFieldID = layer.fieldNameIndex(rowidColumn)
            idFieldID = layer.fieldNameIndex(idColumn)
            ogrfidFieldID = layer.fieldNameIndex(ogrfidColumn)
            
            for key, value in rowidGroupedFeatures.iteritems():
                if value > 1:
                    self.select_features_by_field_value(layer, rowidColumn, key)
                    
                    oldFeatures = []
                    newFeatures = []
                    
                    features = layer.selectedFeatures()
                    
                    for i in xrange(len(features)):
                        if i == 0:
                            continue
                        
                        originalFeature = features[i]
                        
                        oldFeatures.append(originalFeature.id())
                        
                        newFeature = QgsFeature()
                        newFeature.setGeometry(originalFeature.geometry())
                        newFeature.setAttributes(originalFeature.attributes())
                        newFeature.setAttribute(rowidFieldID, None)
                        newFeature.setAttribute(idFieldID, None)
                        newFeature.setAttribute(ogrfidFieldID, None)
                        
                        newFeatures.append(newFeature)
                    
                    layer.deleteFeatures(oldFeatures)
                    layer.addFeatures(newFeatures)
            
            QgsApplication.processEvents()
            
            layer.selectByIds(selectedFeaturesIDs)
        except:
            self.display_error_messages(
                self,
                u'Error in function that ensures unique field values.')

