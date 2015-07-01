# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Humanytek (<http://humanytek.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'HMTK Recursos Humanos',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'summary': "Módulo de Recursos Humanos",
    'description': """
Módulo de Recursos Humanos, personalizado para Interkey

Detalles:
---------
* Agregar campo "Bono" por cada empleado vendedor
    """,
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        # Seguridad y grupos
        
        # Data
        'data/departamentos.xml',
        
        # View y menu
        'view/empleados.xml',
        
        # Reportes
        
    ],
    'demo_xml': [],
    'website': 'https://github.com/humanytek/itk',
    'installable': True,
    'auto_install': False,
    'application': True,
}
