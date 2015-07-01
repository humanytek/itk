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
    'name': 'HMTK Contabilidad/Informe',
    'version': '0.1',
    'sequence': 1,
    'category': 'Custom',
    'complexity': "easy",
    'summary': "Módulo de Comisiones y Bonos",
    'description': """
Módulo de Comisiones y Bonos, personalizado para Interkey

Detalles:
---------
* Crear dependencia del módulo "sfs_payment_comission_glp" con "sale_margin"
* Creación vista de Reportes de bonos, menú: Contabilidad/Informe/Reporte de comisiones/Reporte de bonos
* Creación vista de Reportes de comisiones, menú: Contabilidad/Informe/Reporte de comisiones/Reporte de comisiones
* Cambiar etiqueta "Reglas de penalización" por "Configuración de comisiones"
    """,
    'author': 'Humanytek',
    'website': 'http://humanytek.com',
    'depends': [
        'base',
        'sfs_payment_comission_glp',
        'sale_margin'
    ],
    'data': [
        # Seguridad y grupos
        'security/ir.model.access.csv',
        
        # Data
        
        # View y menu
        'view/reporte_comisiones.xml',
        'view/reporte_bonos.xml',
        'view/configuracion_comisiones.xml',
        
        # Reportes
        
    ],
    'demo_xml': [],
    'website': 'https://github.com/humanytek/itk',
    'installable': True,
    'auto_install': False,
    'application': True,
}
