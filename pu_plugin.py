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

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QToolButton

import resources

from pu_bin import dockwidget
import os.path


class puPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.
        
        Args:
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'puPlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PU Plugin')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolButton = QToolButton()
        self.iface.addToolBarWidget(self.toolButton)

        self.dockWidget = None


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Gets the translation for a string using Qt translation API.
        
        We implement this ourselves since we do not inherit QObject.
        
        Args:
            message (str): String for translation.
        
        Returns:
            QString: Translated version of message.
        
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(u'puPlugin', message)

    def add_action(
            self, icon_path, text, callback,
            enabled_flag=True, add_to_menu=True, add_to_toolbar=True,
            status_tip=None, whats_this=None, parent=None):
        """Adds a toolbar icon to the toolbar.

        Args:
            icon_path (str): Path to the icon for this action.
            text (str): Text that should be shown in menu items for this action.
            callback (function): Function to be called when the action is
                triggered.
            enabled_flag (bool): A flag indicating if the action should be
                enabled by default. Defaults to True.
            add_to_menu (bool): Flag indicating whether the action should also
                be added to the menu. Defaults to True.
            add_to_toolbar (bool): Flag indicating whether the action should
                also be added to the toolbar. Defaults to True.
            status_tip (str): Optional text to show in a popup when mouse
                pointer hovers over the action.
            parent (QWidget): Parent widget for the new action. Defaults None.
            whats_this (str): Optional text to show in the status bar when the
                mouse pointer hovers over the action.
        
        Returns:
            QAction: The action that was created. Note that the action is also
                added to self.actions list.
        
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)

        self.toolButton.setDefaultAction(action)

        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            pass

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PU Plugin'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        self.dockWidget = dockwidget.DockWidget(self.iface)
        
        self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockWidget)
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        
        for action in self.actions:
            self.iface.removePluginMenu(u'&PU Plugin', action)
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        
        self.iface.removeDockWidget(self.dockWidget)
    
    def run(self):
        """Show the dockWidget if visible, otherwise hides the dockWidget."""
        
        if not self.dockWidget.isVisible():
            self.dockWidget.show()
        else:
            self.dockWidget.hide()

