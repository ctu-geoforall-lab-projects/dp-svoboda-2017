# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ToolBarWidget
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

from PyQt4.QtGui import (QWidget, QHBoxLayout, QHBoxLayout, QToolBar, QAction,
                         QIcon, QPixmap)
from PyQt4.QtCore import QSize


class ToolBarWidget(QWidget):
    """A widget which contains tools."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dW = dockWidgetName
        self.iface = iface
        
        super(QWidget, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'toolBarWidget')
        
        self.toolBarHBoxLayout = QHBoxLayout(self)
        self.toolBarHBoxLayout.setObjectName(u'toolBarHBoxLayout')
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Build own widgets."""
        
        self.toolBar = QToolBar(self)
        self.toolBar.setObjectName(u'toolBar')
        self.toolBar.resize(QSize(100, 40))
        self.toolBar.setIconSize(QSize(26, 26))
        self.toolBarHBoxLayout.addWidget(self.toolBar)
        
        self.selectRectangleAction = QAction(self.toolBar)
        self.selectRectangleAction.setObjectName(u'selectRectangleAction')
        selectRectangleIcon = QIcon()
        selectRectangleIcon.addPixmap(QPixmap(':/mActionSelectRectangle.svg'))
        self.selectRectangleAction.setIcon(selectRectangleIcon)
        self.toolBar.addAction(self.selectRectangleAction)
        
        self.selectPolygonAction = QAction(self.toolBar)
        self.selectPolygonAction.setObjectName(u'selectPolygonAction')
        selectPolygonIcon = QIcon()
        selectPolygonIcon.addPixmap(QPixmap(':/mActionSelectPolygon.svg'))
        self.selectPolygonAction.setIcon(selectPolygonIcon)
        self.toolBar.addAction(self.selectPolygonAction)

