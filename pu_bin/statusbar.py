# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StatusBar
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

from PyQt4.QtGui import QStatusBar
from PyQt4.QtCore import QSettings


class StatusBar(QStatusBar):
    """A status bar for displaying messages."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
            iface (QgisInterface): A reference to the QgisInterface.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        super(StatusBar, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'statusbar')
        
        self.frameText = QSettings()
        
        self.setStyleSheet("border: none")
    
    def set_text_statusbar(self, text, duration):
        """Sets text.
        
        Args:
            text (str): A text to be written.
            duration (int): A duration of the message in seconds.
        
        """
        
        sender = self.sender().objectName()
        
        if duration == 0:
            self.frameText.setValue(sender, text)
        else:
            self.frameText.setValue(sender, '')
        
        duration *= 1000
        
        self.showMessage(text, duration)
    
    def change_text_statusbar(self):
        """Changes text according to the active tab."""
        
        currentWidgetName = self.dW.stackedWidget.currentWidget().objectName()
        
        text = self.frameText.value(currentWidgetName, '')
        
        self.showMessage(text)

