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

from PyQt4.QtGui import (QDockWidget, QWidget, QGridLayout, QStatusBar,
                         QFileDialog)
from PyQt4.QtCore import pyqtSignal, QSettings

from qgis.gui import QgsMessageBar
from qgis.core import *

from collections import namedtuple

from statusbar import Statusbar
from toolbar import Toolbar
from stackedwidget import StackedWidget

import traceback


class DockWidget(QDockWidget):
    """The main widget of the PU Plugin."""
    
    text_statusbar = pyqtSignal(str, int)
    
    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.iface = iface
        
        self.editablePuColumnsPAR = (
            'PU_KMENOVE_CISLO_PAR',
            'PU_PODDELENI_CISLA_PAR')
        
        self.visiblePuColumnsPAR = \
            self.editablePuColumnsPAR + \
            ('PU_VYMERA_PARCELY', 'PU_VZDALENOST', 'PU_CENA')
        
        self.allPuColumnsPAR = self.visiblePuColumnsPAR + ('PU_KATEGORIE',)
        
        self.columnsPAR = (
            'KMENOVE_CISLO_PAR',
            'PODDELENI_CISLA_PAR',
            'VYMERA_PARCELY')
        
        self.visibleColumnsPAR = self.visiblePuColumnsPAR + self.columnsPAR
        
        self.rqdColumnsPAR = self.allPuColumnsPAR + self.columnsPAR
        
        super(DockWidget, self).__init__()
        
        dockWidgetName = u'dockWidget'
        
        self._setup_self(dockWidgetName)
       
    def _setup_self(self, dockWidgetName):
        """Sets up self.
        
        Args:
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.setObjectName(u'dockWidget')
        
        self.settings = QSettings()
        
        self.mainWidget = QWidget(self)
        self.mainWidget.setObjectName(u'mainWidget')
        
        self.setWidget(self.mainWidget)
        
        self.mainGridLayout = QGridLayout(self.mainWidget)
        self.mainGridLayout.setObjectName(u'mainGridLayout')
        
        self.setWindowTitle(u'PU Plugin')
        
        self._build_widgets(dockWidgetName)
    
    def _build_widgets(self, dockWidgetName):
        """Builds own widgets.
        
        Args:
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.toolbar = Toolbar(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.toolbar, 0, 0, 1, 1)
        
        self.statusbar = Statusbar(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.statusbar, 2, 0, 1, 1)
        
        self.text_statusbar.connect(self.statusbar.set_text_statusbar)
        
        self.stackedWidget = StackedWidget(self, dockWidgetName, self.iface)
        self.mainGridLayout.addWidget(self.stackedWidget, 1, 0, 1, 1)
    
    def _raise_pu_error(
            self, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
        """Displays error messages.
    
        Displays error messages in the Log Messages Panel, statusLabel
        and Message Bar.
        
        For development purposes it displays traceback
        in the 'puPlugin Development' Log Messages Tab.
        
        Args:
            engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
            czeLabelMsg (str): A message in the statusLabel.
            czeBarMsg (str): A message in the Message Bar.
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
        self.text_statusbar.emit(czeLabelMsg, duration*1000)
        self.iface.messageBar().pushMessage(
            pluginName, czeBarMsg , QgsMessageBar.WARNING, duration)
        
        developmentTb = u'PU Plugin Development'
        tb = traceback.format_exc()
        
        QgsMessageLog.logMessage(tb, developmentTb)
    
    def _get_settings(self, key):
        """Returns value for settings key.
        
        Args:
            key (str): A settings key.
                
        Returns:
            str: A value for settings key.
        
        """
        
        value = self.settings.value(key, '')
        
        return value
    
    def _set_settings(self, key, value):
        """Sets value for settings key.
        
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
            existence (bool): True when the file has to exist
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
    
    def check_active_layer(self, sender):
        """Checks active layer.
        
        First it checks if there is an active layer, then if the active layer
        is vector and finally if the active layer contains all required columns.
        
        Args:
            sender (object): A reference to the sender object.
        
        Returns:
            namedtuple: First element is True when there is an active vector
                layer that contains all required columns, False otherwise.
                Second element called 'layer' is a reference
                to the active layer.
        
        """
        
        SuccessLayer = namedtuple('successLayer', ['success', 'layer'])
        
        layer = self.iface.activeLayer()
        
        if not layer:
            sender.text_statusbar.emit(u'Žádná aktivní vrstva.', 7000)
            successLayer = SuccessLayer(False, layer)
            return successLayer
        
        if layer.type() != 0:
            sender.text_statusbar.emit(u'Aktivní vrstva není vektorová.', 7000)
            successLayer = SuccessLayer(False, layer)
            return successLayer
        
        fieldNames = [field.name() for field in layer.pendingFields()]
        
        if not all(column in fieldNames for column in self.rqdColumnsPAR):
            sender.text_statusbar.emit(
                u'Aktivní vrstva neobsahuje potřebné sloupce.', 7000)
            successLayer = SuccessLayer(False, layer)
            return successLayer
        
        successLayer = SuccessLayer(True, layer)
        return successLayer
    
    def check_editing(self):
        """Checks if editing is enabled.
        
        Returns:
            bool: True when editing is enabled, False otherwise.
        
        """
        
        if self.stackedWidget.editFrame.toggleEditingAction.isChecked():
            return True
        else:
            return False
    
    def select_features_by_field_and_value(self, layer, field, value):
        """Selects features in given layer by the value and field.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
            field (str): A name of the field.
            value (str) A value of the field.
        
        """
        
        expression = QgsExpression("\"{}\" = {}".format(field, value))
        
        features = layer.getFeatures(QgsFeatureRequest(expression))
        
        featuresID = [feature.id() for feature in features]
        
        layer.selectByIds(featuresID)
    
    class puError(Exception):
        """A custom exception."""
        
        def __init__(
                self, dW, engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7):
            """Constructor.
            
            Args:
                dW (QWidget): A reference to the dock widget.
                engLogMsg (str): A message in the 'puPlugin' Log Messages Panel.
                czeLabelMsg (str): A message in the statusLabel.
                czeBarMsg (str): A message in the Message Bar.
                duration (int): A duration of the message in the Message Bar
                                 in seconds.
                
            """
            
            super(Exception, self).__init__(dW)
            
            self.dW = dW
            
            self.dW._raise_pu_error(
                engLogMsg, czeLabelMsg, czeBarMsg=None, duration=7)

