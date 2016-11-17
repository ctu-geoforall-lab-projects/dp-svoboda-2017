# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Executehread
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

from PyQt4.QtCore import QThread, pyqtSignal


class Executehread(QThread):
    """A subclass of QThread for executing processes."""
    
    work = pyqtSignal(object)

    def __init__(self, layer):
        """Constructor.
        
        Args:
            layer (QgsVectorLayer): A reference to the layer.
        
        """
        
        super(Executehread, self).__init__()

        self.layer = layer

    def run(self):
        """Starts the QThread and emits self.layer."""
        
        self.work.emit(self.layer)

