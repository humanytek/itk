# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 Humanytek. http://www.humanytek.com
#    soporte@humanytek.com
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

from openerp.osv import osv, fields
import tools
import openerp.addons.decimal_precision as dp
from datetime import datetime, date, timedelta

import logging
_logger = logging.getLogger(__name__)

class payment_bonos_report_itk(osv.Model):

    _name = 'payment.bonos.report'
    _description = 'Campos para reporte de bonos'
    
    # 21/05/2015 (felix) Metodo para calculo monto de venta al mes
    def _calc_monto_venta(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            for j in i.facturas_ids:
                res[i.id] += j.monto_factura
        return res
        
    # 21/05/2015 (felix) Metodo para calculo de monto a pagar
    def _calc_monto_pago(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        obj_rule_bono = self.pool.get('bono.rule.line')
        all_rule_bono = obj_rule_bono.search(cr, uid, [(1, '=', 1)])
        for i in self.browse(cr, uid, ids, context):
            res[i.id] = 0.00
            sub_total = 0.00
            for j in i.facturas_ids:
                sub_total += j.monto_factura
            for b in obj_rule_bono.browse(cr, uid, all_rule_bono, context):
                if sub_total >= b.monto_venta:
                    res[i.id] += b.monto_pago
        return res
    
    _columns = {
        'name': fields.char('Bono', size=1024),
        'vendedor_id': fields.many2one('res.users', 'Vendedor'),
        'fecha_pago': fields.date('Fecha pago de bono'),
        'monto_venta': fields.function(_calc_monto_venta, type='float', 
            string='Monto venta al mes'),
        'monto_pago': fields.function(_calc_monto_pago, type='float', 
            string='Monto de bono'),
        'state': fields.selection([('open', 'Abierto'), ('close', 'Pagado'), 
            ('na', 'N/A')], 'Estatus'),
        'facturas_ids': fields.one2many('payment.bonos.report.line', 'bono_id', 
            'Facturas'),
    }
    _order = 'name desc'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Este campo debe ser unico')
    ]
    
    # 20/05/2015 (felix) Generacion de nombre de bono
    def _gen_name_bono(self, cr, uid, user_id, fecha_factura, context=None):
        res = ''
        fecha_factura = str(fecha_factura).split('-')
        ano = datetime.now().year
        mes = datetime.now().month
        obj_users = self.pool.get('res.users')
        get_users = obj_users.search(cr, uid, [('id', '=', user_id)])
        login = obj_users.browse(cr, uid, get_users[0], context)['login']
        res = str(login).upper()+'/'+str(fecha_factura[0])+'/'+str(fecha_factura[1]).rjust(2,'0')        
        return res
                    
    # 18/05/2015 (felix) Metodo para mostrar listado de bonos
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        # Actualizar tabla de bonos
        obj_account_invoice = self.pool.get('account.invoice')
        all_account_invoice = obj_account_invoice.search(cr, uid, [(1, '=', 1)])
        obj_account_move_line = self.pool.get('account.move.line')
        obj_bonos_report = self.pool.get('payment.bonos.report')
        obj_bonos_report_line = self.pool.get('payment.bonos.report.line')
        obj_bono_rule = self.pool.get('bono.rule.line')
        
        for inv in obj_account_invoice.browse(cr, uid, all_account_invoice, context):
            if inv.user_id.bono is True and inv.state in 'paid':
                
                cant_prod = 0
                for inv_line in inv.invoice_line:
                    cant_prod += 1
                    
                src_pagos = obj_account_move_line.search(cr, uid, [('move_id', 'like', inv.move_id.id)], order='id desc', limit=1)
                fecha_pago_factura = obj_account_move_line.browse(cr, uid, src_pagos[0], context)['date']
                name_bono = self._gen_name_bono(cr, uid, inv.user_id.id, fecha_pago_factura, context)
                get_bono = obj_bonos_report.search(cr, uid, [('name', '=', name_bono)])
                
                if not get_bono:
                    value_bono = {
                        'vendedor_id': inv.user_id.id,
                        'name': name_bono,
                        'state': 'open'
                    }
                    bono_id = obj_bonos_report.create(cr, uid, value_bono, context)
                    value_factura = {
                        'factura_id': inv.id,
                        'cliente_id': inv.user_id.id,
                        'fecha_factura': inv.date_invoice,
                        'fecha_pago': fecha_pago_factura,
                        'cant_productos': cant_prod,
                        'monto_factura': inv.amount_total,
                        'bono_id': bono_id
                    }
                    obj_bonos_report_line.create(cr, uid, value_factura, context)
                else:
                    src_bono_line = obj_bonos_report_line.search(cr, uid, [('factura_id', '=', inv.id)])
                    if not src_bono_line:
                        bono_id = obj_bonos_report.browse(cr, uid, get_bono[0], context)['id']
                        value_factura = {
                            'factura_id': inv.id,
                            'cliente_id': inv.user_id.id,
                            'fecha_factura': inv.date_invoice,
                            'fecha_pago': fecha_pago_factura,
                            'cant_productos': cant_prod,
                            'monto_factura': inv.amount_total,
                            'bono_id': bono_id
                        }
                        obj_bonos_report_line.create(cr, uid, value_factura, context)
        
        # Revisar cantidad de bono y cambiar estado si no aplica pago de bono
        all_bono = self.search(cr, uid, [(1, '=', 1)])
        for bono in self.browse(cr, uid, all_bono, context):
            if bono.state in 'open' and bono.monto_pago == 0.00:
                self.write(cr, uid, bono.id, {'state':'na'}, context)
            elif bono.state in 'na' and bono.monto_pago > 0.00:
                self.write(cr, uid, bono.id, {'state':'open'}, context)
        
        res = super(payment_bonos_report_itk,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res
    
    # 21/05/2015 (felix) Metodo para registro de pago del bono
    def close_bono(self, cr, uid, ids, context=None):
        if ids:
            state = self.browse(cr, uid, ids[0], context)['state']
            if state in 'open':
                fecha_pago = datetime.now().date()
                values = {
                    'state': 'close',
                    'fecha_pago': fecha_pago
                }
                self.write(cr, uid, ids[0], values, context)
                return True
        return False
    
payment_bonos_report_itk()


class payment_bonos_report_line_itk(osv.Model):

    _name = 'payment.bonos.report.line'
    _description = 'Campos para lista de facturas en reporte de bonos'
    _columns = {
        'factura_id': fields.many2one('account.invoice', 'Factura'),
        'cliente_id': fields.many2one('res.partner', 'Cliente'),
        'fecha_factura': fields.date('Fecha de factura'),
        'fecha_pago': fields.date('Fecha de pago'),
        'cant_productos': fields.integer('Cantidad de productos por linea'),
        'monto_factura': fields.float('Monto de la factura', digits=(10,2)),
        'bono_id': fields.many2one('payment.bonos.report', 'Bono')
    }
    _rec_name = 'factura_id'
    _order = 'id desc'
    
payment_bonos_report_line_itk()
