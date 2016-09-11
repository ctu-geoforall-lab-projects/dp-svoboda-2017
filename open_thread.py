# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenThread
                                 A QGIS plugin
 Plugin pro pozemkové úpravy
                             -------------------
        begin                : 2016-09-04
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


class OpenThread(QThread):
    """A subclass of QThread with pyqtSignal called work."""

    def __init__(self):
        """Constructor."""
        
        super(OpenThread, self).__init__()
        
    work = pyqtSignal()

    def run(self):
        self.work.emit()

