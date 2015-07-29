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
    'name': 'HMTK Contabilidad/Clientes',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'summary': "Módulo de Contabilidad, sección Clientes",
    'description': """
Módulo de Contabilidad/Clientes, personalizado para Interkey

Detalles:
---------
* Agregar columna "Precio coste" de producto en Facturas de cliente
    """,
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': [
        'base',
        'account',
        'account_voucher',
        'sale',
        'sfs_payment_comission_glp'
    ],
    'data': [
        # Seguridad y grupos
        #'security/ir.model.access.csv',
        
        # Data
        
        # View y menu
        'view/facturas_cliente.xml',
        
        # Wizard
        
        # Reportes
        
    ],
    'demo_xml': [],
    'website': 'https://github.com/humanytek/itk',
    'installable': True,
    'auto_install': False,
    'application': True,
}
