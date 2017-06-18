# -*- coding: utf-8 -*-
"""
/***************************************************************************
 puPlugin
                                 A QGIS plugin
 Plugin pro pozemkové úpravy
                             -------------------
        begin                : 2016-09-01
        copyright            : (C) 2016 by Ondřej Svoboda
        email                : svoboond@gmail.com
        git sha              : $Format:%H$
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


def classFactory(iface):
    """Loads puPlugin class.
    
    Args:
        iface (QgisInterface): A reference to the QgisInterface.

    Returns:
        class: The main class of the PU Plugin.
    
    """
    
    from puplugin import puPlugin
    return puPlugin(iface)
