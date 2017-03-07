# -*- coding: utf-8 -*-
"""
/***************************************************************************
 puPlugin
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

from PyQt4.QtGui import QAction, QIcon, QToolButton, QPixmap
from PyQt4.QtCore import QDir, Qt

import os

from pubin import dockwidget


class puPlugin(object):
    """The main class of the PU Plugin."""

    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.iface = iface
        
        self.name = u'PU Plugin'

        self.pluginDir = QDir(os.path.dirname(__file__))
    
    def initGui(self):
        """Initializes GUI."""
        
        iconsDir = QDir(self.pluginDir.path() + u'/data/icons')
        
        self.puAction = QAction(self.iface.mainWindow())
        self.puAction.setText(self.name)
        puIcon = QIcon()
        puIcon.addPixmap(QPixmap(iconsDir.filePath(u'puplugin.png')))
        self.puAction.setIcon(puIcon)
        self.puAction.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.puAction)
        self.iface.addPluginToMenu(self.name, self.puAction)
        
        self.dockWidget = dockwidget.DockWidget(
            self.iface, self.pluginDir, self.name)
        
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget)
    
    def unload(self):
        """Removes the plugin menu and icon."""
        
        self.dockWidget.disconnect_from_iface()
        
        self.iface.removePluginMenu(self.name, self.puAction)
        self.iface.removeToolBarIcon(self.puAction)
        
        self.iface.removeDockWidget(self.dockWidget)
    
    def run(self):
        """Shows the dockWidget if not visible, otherwise hides it."""
        
        if not self.dockWidget.isVisible():
            self.dockWidget.show()
        else:
            self.dockWidget.hide()

