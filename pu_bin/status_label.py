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
from PyQt4.QtCore import pyqtSignal


class StatusLabel(QLabel):
    """A label for displaying messages."""
    
    text_statusLabel = pyqtSignal(str)
    
    def __init__(self, parentWidget, dockWidgetName, iface):
        """Constructor.
        
        Args:
            parentWidget (QWidget): A reference to the parent widget.
            dockWidgetName (str): A name of the dock widget.
        
        """
        
        self.pW = parentWidget
        self.dW = dockWidgetName
        self.iface = iface
        
        super(QLabel, self).__init__(self.pW)
        
        self._setup_self()
    
    def _setup_self(self):
        """Sets up self."""
        
        self.setObjectName(u'statusLabel')
        self.text_statusLabel.connect(self._set_text_statusLabel)
        self.text_statusLabel.emit(u'Vyberte VFK soubor.')
    
    def _set_text_statusLabel(self, text):
        """Sets text.
        
        Args:
            text (str): A text to be written.
        
        """
    
        self.setText(text)

     