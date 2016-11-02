# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StatusLabel
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

from PyQt4.QtGui import QLabel
from PyQt4.QtCore import QSettings


class StatusLabel(QLabel):
    """A label for displaying messages."""
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.dW = parentWidget
        self.dWName = dockWidgetName
        self.iface = iface
        
        super(QLabel, self).__init__(self.dW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'statusLabel')
        
        self.frameText = QSettings()
    
    def _set_text_statusLabel(self, text):
        """Sets text.
        
        Args:
            text (str): A text to be written.
        
        """
        
        sender = self.sender().objectName()
        
        self.frameText.setValue('puplugin/' + sender, text)
        
        self.setText(text)
    
    def _change_text_statusLabel(self):
        """Changes text according to the active tab."""
        
        currentWidgetName = self.dW.stackedWidget.currentWidget().objectName()
        
        self.setText(self.frameText.value('puplugin/' + currentWidgetName, ''))

