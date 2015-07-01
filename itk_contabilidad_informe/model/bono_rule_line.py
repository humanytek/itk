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


class bono_rule_line_itk(osv.Model):

    _name = 'bono.rule.line'
    _description = 'Tabla para registro de referencias de bonos'
    _columns = {
        'monto_venta': fields.float('Monto de venta al mes', digits=(10,2)),
        'monto_pago': fields.float('Monto a pagar', digits=(10,2)),
        'bono_id': fields.many2one('penalization.rule', 'Penalization', 
            ondelete='cascade')
    }
    _rec_name = 'monto_venta'
    
bono_rule_line_itk()
