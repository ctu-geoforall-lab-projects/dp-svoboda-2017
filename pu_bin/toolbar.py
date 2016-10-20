# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Toolbar
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

from PyQt4.QtGui import (QHBoxLayout, QHBoxLayout, QToolBar, QAction,
                         QIcon, QPixmap)
from PyQt4.QtCore import QSize, pyqtSignal, pyqtSlot, SIGNAL, SLOT

from qgis.core import *


class Toolbar(QToolBar):
    """A widget which contains tools."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QToolBar): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dW = dockWidgetName
        self.iface = iface
        
        super(QToolBar, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'toolBar')
        self.setIconSize(QSize(24, 24))
        
        self.toolBarHBoxLayout = QHBoxLayout(self)
        self.toolBarHBoxLayout.setObjectName(u'toolBarHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.selectRectangleAction = QAction(self)
        self.selectRectangleAction.setObjectName(u'selectRectangleAction')
        self.actionSelectRectangle = self.iface.actionSelectRectangle()
        self.actionSelectRectangle.changed.connect(
            self._change_selectRectangleAction)
        self.selectRectangleAction.triggered.connect(
            self._trigger_selectRectangleAction)
        self.selectRectangleAction.setCheckable(True)
        if self.actionSelectRectangle.isChecked():
            self.selectRectangleAction.setChecked(True)
        if not self.actionSelectRectangle.isEnabled():
            self.selectRectangleAction.setDisabled(True)
        selectRectangleIcon = QIcon()
        selectRectangleIcon.addPixmap(QPixmap(':/mActionSelectRectangle.svg'))
        self.selectRectangleAction.setIcon(selectRectangleIcon)
        self.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = QAction(self)
        self.selectPolygonAction.setObjectName(u'selectPolygonAction')
        self.actionSelectPolygon = self.iface.actionSelectPolygon()
        self.actionSelectPolygon.changed.connect(
            self._change_selectPolygonAction)
        self.selectPolygonAction.triggered.connect(
            self._trigger_selectPolygonAction)
        self.selectPolygonAction.setCheckable(True)
        if self.actionSelectPolygon.isChecked():
            self.selectPolygonAction.setChecked(True)
        if not self.actionSelectPolygon.isEnabled():
            self.selectPolygonAction.setDisabled(True)
        selectPolygonIcon = QIcon()
        selectPolygonIcon.addPixmap(QPixmap(':/mActionSelectPolygon.svg'))
        self.selectPolygonAction.setIcon(selectPolygonIcon)
        self.addAction(self.selectPolygonAction)
    
    def _change_selectRectangleAction(self):
        """Sets selectRectangleAction based on QGIS actionSelectRectangle."""
        
        if self.actionSelectRectangle.isEnabled():
            self.selectRectangleAction.setEnabled(True)
        else:
            self.selectRectangleAction.setDisabled(True)
        
        if self.actionSelectRectangle.isChecked():
            self.selectRectangleAction.setChecked(True)
        else:
            self.selectRectangleAction.setChecked(False)
    
    def _trigger_selectRectangleAction(self):
        """Triggers select by rectangle."""
        
        if not self.selectRectangleAction.isChecked():
            self.selectRectangleAction.setChecked(True)
            
        if not self.actionSelectRectangle.isChecked():
            self.actionSelectRectangle.trigger()
    
    def _change_selectPolygonAction(self):
        """Sets selectPolygonAction based on QGIS actionSelectPolygon."""
        
        if self.actionSelectPolygon.isEnabled():
            self.selectPolygonAction.setEnabled(True)
        else:
            self.selectPolygonAction.setDisabled(True)
        
        if self.actionSelectPolygon.isChecked():
            self.selectPolygonAction.setChecked(True)
        else:
            self.selectPolygonAction.setChecked(False)
    
    def _trigger_selectPolygonAction(self):
        """Triggers select by polygon."""
        
        if not self.selectPolygonAction.isChecked():
            self.selectPolygonAction.setChecked(True)
        
        if not self.actionSelectPolygon.isChecked():
            self.actionSelectPolygon.trigger()

