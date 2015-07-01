# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 SF Soluciones.
#    (http://www.sfsoluciones.com)
#    contacto@sfsoluciones.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class penalization_rule_itk(osv.Model):

    _inherit = 'penalization.rule'
    _descritpion = 'Campos adicionales para modulo de comisiones'
    _columns = {
        'bono_line_ids': fields.one2many('bono.rule.line', 'bono_id', 
            'Penalization Rules'),
        'monto_tolerancia': fields.float('Monto tolerancia pago', digits=(10,2)),
        'porcentaje_comision': fields.float('Porcentaje de comision', 
            digits=(3,2))
    }
    
penalization_rule_itk()
