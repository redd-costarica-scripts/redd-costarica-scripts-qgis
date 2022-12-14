# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Redd_CostaRica
                                 A QGIS plugin
 Redd+ Costa Rica
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-09-18
        copyright            : (C) 2022 by Manuel Vargas
        email                : mfvargas@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Manuel Vargas'
__date__ = '2022-09-18'
__copyright__ = '(C) 2022 by Manuel Vargas'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Redd_CostaRica class from file Redd_CostaRica.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .redd_costarica import Redd_CostaRicaPlugin
    return Redd_CostaRicaPlugin()
