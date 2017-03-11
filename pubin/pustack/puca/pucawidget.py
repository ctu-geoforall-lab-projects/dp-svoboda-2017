# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PuCaWidget
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

from PyQt4.QtGui import QWidget, QVBoxLayout
from PyQt4.QtCore import Qt


class PuCaWidget(QWidget):
    """A subclass of QWidget."""
    
    def __init__(
            self,
            parentWidget, dockWidgetName, iface, dockWidget, pluginDir,
            objectName):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
            dockWidget (QWidget): A reference to the dock widget.
            pluginDir (QDir): A plugin directory.
            objectName (str): A name of the object.
        
        """
        
        self.pW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        self.dW = dockWidget
        self.pluginDir = pluginDir
        
        super(PuCaWidget, self).__init__(self.pW)
        
        self._setup_self(objectName)
    
    def _setup_self(self, objectName):
        """Sets up self.
        
        Args:
            objectName (str): A name of the object.
        
        """
        
        self.setObjectName(objectName)
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setObjectName(u'vBoxLayout')
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        self._build_widgets()
    
    def _build_widgets(self):
        """Builds own widgets."""
        
        raise NotImplementedError

