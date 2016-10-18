# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LoadThread
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


class LoadThread(QThread):
    """A subclass of QThread for loading a VFK file."""
    
    work = pyqtSignal(str)

    def __init__(self, filePath):
        """Constructor.
        
        Args:
            filePath (str): A full path to the file.
        
        """
        
        super(LoadThread, self).__init__()

        self.filePath = filePath

    def run(self):
        """Starts the QThread and emits self.filePath."""
        
        self.work.emit(self.filePath)

