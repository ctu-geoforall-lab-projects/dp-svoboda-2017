# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StackedWidget
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

from PyQt4.QtGui import QStackedWidget
from PyQt4.QtCore import QSignalMapper

from collections import namedtuple

from pu_stackedwidget_frames import (loadvfk_frame, edit_frame,
                                     check_analysis_frame)


class StackedWidget(QStackedWidget):
    """A stacked widget that stores several other widgets."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        self.editablePuColumnsPAR = (
            'PU_KMENOVE_CISLO_PAR',
            'PU_PODDELENI_CISLA_PAR')
        
        self.visiblePuColumnsPAR = \
            self.editablePuColumnsPAR + ('PU_VYMERA_PARCELY', 'PU_VZDALENOST')
        
        self.allPuColumnsPAR = self.visiblePuColumnsPAR + ('PU_KATEGORIE',)
        
        self.columnsPAR = (
            'KMENOVE_CISLO_PAR',
            'PODDELENI_CISLA_PAR',
            'VYMERA_PARCELY')
        
        self.visibleColumnsPAR = self.visiblePuColumnsPAR + self.columnsPAR
        
        self.rqdColumnsPAR = self.allPuColumnsPAR + self.columnsPAR
        
        super(QStackedWidget, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'stackedWidget')
        
        self.openTabSignalMapper = QSignalMapper(self)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        self.loadVfkFrame = loadvfk_frame.LoadVfkFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.loadVfkFrame)
        self.dW.toolbar.loadVfkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.loadVfkAction, 0)
        
        self.editFrame = edit_frame.EditFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.editFrame)
        self.dW.toolbar.editAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.editAction, 1)
        
        self.checkAnalysisFrame = check_analysis_frame.CheckAnalysisFrame(
            self, self.dWName, self.iface, self.dW)
        self.addWidget(self.checkAnalysisFrame)
        self.dW.toolbar.checkAction.triggered.connect(
            self.openTabSignalMapper.map)
        self.openTabSignalMapper.setMapping(self.dW.toolbar.checkAction, 2)
        
        self.openTabSignalMapper.mapped.connect(self.setCurrentIndex)
        
        self.currentChanged.connect(
            self.dW.statusbar._change_text_statusbar)
    
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

