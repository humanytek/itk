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


class payment_comission_main_itk(osv.osv):

    _name = 'payment.comission.main'
    _description = 'Campos principales para vistas de reporte de comisiones'
        
    # 25/05/2015 (felix) Metodo para calculo monto de venta al mes
    def _calc_monto_penalizacion(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            for linea in com.facturas_ids:
                res[com.id] += linea.penalization_amount
        return res
        
    # 25/05/2015 (felix) Metodo para calculo de monto a pagar
    def _calc_monto_comision(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            for linea in com.facturas_ids:
                res[com.id] += linea.comision_penalizacion
        return res
    
    # 27/05/2015 (felix) Metodo para contar el numero de facturas por comisiones
    def _get_cant_facturas(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0
            for fac in com.facturas_ids:
                res[com.id] += 1
        return res
            
    _columns = {
        'name': fields.char('Comision', size=1024),
        'vendedor_id': fields.many2one('res.users', 'Vendedor'),
        'fecha_pago': fields.date('Fecha pago de comision'),
        'monto_penalizacion': fields.function(_calc_monto_penalizacion, 
            type='float', string='Monto pensalizacion'),
        'monto_comision': fields.function(_calc_monto_comision, type='float', 
            string='Monto comision'),
        'cant_facturas': fields.function(_get_cant_facturas, type='integer', 
            string='Cantidad de facturas'),
        'facturas_ids': fields.one2many('payment.comission.line', 'comision_id', 
            'Facturas'),
        'state': fields.selection([('open', 'Abierta'), ('close', 'Pagada'), 
            ('na', 'N/A')], 'Estatus')
    }
    _order = 'name desc'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Este campo debe ser unico')
    ]
    
    # 20/05/2015 (felix) Generacion de nombre de bono
    def _gen_name_comision(self, cr, uid, user_id, fecha_factura, context=None):
        res = ''
        fecha_factura = str(fecha_factura).split('-')
        obj_users = self.pool.get('res.users')
        get_users = obj_users.search(cr, uid, [('id', '=', user_id)])
        login = obj_users.browse(cr, uid, get_users[0], context)['login']
        if int(fecha_factura[2]) < 16:
            res = str(login).upper()+'/'+str(fecha_factura[0])+'/'+str(fecha_factura[1]).rjust(2,'0')+'_1'
        else:
            res = str(login).upper()+'/'+str(fecha_factura[0])+'/'+str(fecha_factura[1]).rjust(2,'0')+'_2'
        return res
                    
    # 25/05/2015 (felix) Metodo para mostrar listado de bonos
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        # Actualizar tabla de comisiones
        obj_account_invoice = self.pool.get('account.invoice')
        all_account_invoice = obj_account_invoice.search(cr, uid, [(1, '=', 1)])
        obj_account_move = self.pool.get('account.move')
        obj_account_move_line = self.pool.get('account.move.line')
        obj_comision_report = self.pool.get('payment.comission.main')
        obj_comision_report_line = self.pool.get('payment.comission.line')
        obj_comision_rule = self.pool.get('penalization.rule')
        obj_comision_rule_line = self.pool.get('penalization.rule.line')
        
        cant_facturas = 0
        
        # 31/07/2015 (felix) Repasar facturas que fueron canceladas y borrarlas
        src_invoice_cancel = obj_account_invoice.search(cr, uid, [('state','=','cancel')])
        for inv_cancel in obj_account_invoice.browse(cr, uid, src_invoice_cancel, context):
            src_comision_cancel = obj_comision_report_line.search(cr, uid, [('invoice_id','=',inv_cancel.id)])
            if src_comision_cancel:
                id_inv_cancel = obj_comision_report_line.browse(cr, uid, src_comision_cancel[0], context)['id']
                obj_comision_report_line.unlink(cr, uid, [id_inv_cancel], context)
        
        # Capturar datos de regla de penalizacion activa
        src_comision_rule = obj_comision_rule.search(cr, uid, [('active', '=', True)], order='id desc', limit=1)
        if src_comision_rule:
            tolerancia = obj_comision_rule.browse(cr, uid, src_comision_rule[0], context)['monto_tolerancia']
        else:
            raise osv.except_osv('Advertencia','No se ha creado una configuracion de comision\ndebe configurarla en:\n'
                'Contabilidad/Configuracion/Configuracion de comisiones')
            return {}
        
        for inv in obj_account_invoice.browse(cr, uid, all_account_invoice, context):
                        
            if inv.user_id and inv.type in ['out_invoice'] and inv.state in ['open','paid'] and inv.residual <= tolerancia:
            
                src_pagos = obj_account_move_line.search(cr, uid, [('name','like',inv.number)], order='id desc', limit=1)
                if src_pagos:
                    fecha_pago_factura = obj_account_move_line.browse(cr, uid, src_pagos[0], context)['date']
                name_comision = self._gen_name_comision(cr, uid, inv.user_id.id, fecha_pago_factura, context)
                get_comision = obj_comision_report.search(cr, uid, [('name', '=', name_comision)])
                
                if not get_comision:
                    cant_facturas += 1
                    value_comision = {
                        'vendedor_id': inv.user_id.id,
                        'name': name_comision,
                        'state': 'open'
                    }
                    comision_id = obj_comision_report.create(cr, uid, value_comision, context)
                    value_factura = {
                        'invoice_id': inv.id,
                        'partner_id': inv.partner_id.id,
                        'fecha_creacion': inv.date_invoice,
                        'due_date': inv.date_due,
                        'payment_date': fecha_pago_factura,
                        'payment_term_id': inv.payment_term.id,
                        'comision_id': comision_id,
                        'invoice_amount': inv.amount_total,
                        'amount_tax': inv.amount_tax,
                        'amount_untaxed': inv.amount_untaxed,
                        'state': inv.state
                    }
                    obj_comision_report_line.create(cr, uid, value_factura, context)
                else:
                    src_comision_line = obj_comision_report_line.search(cr, uid, [('invoice_id', '=', inv.id)])
                    if not src_comision_line:
                        comision_id = obj_comision_report.browse(cr, uid, get_comision[0], context)['id']
                        value_factura = {
                            'invoice_id': inv.id,
                            'partner_id': inv.partner_id.id,
                            'fecha_creacion': inv.date_invoice,
                            'due_date': inv.date_due,
                            'payment_date': fecha_pago_factura,
                            'payment_term_id': inv.payment_term.id,
                            'comision_id': comision_id,
                            'invoice_amount': inv.amount_total,
                            'amount_tax': inv.amount_tax,
                            'amount_untaxed': inv.amount_untaxed,
                            'state': inv.state
                        }
                        obj_comision_report_line.create(cr, uid, value_factura, context)
        
        res = super(payment_comission_main_itk,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, 
            context=context, toolbar=toolbar, submenu=submenu)
        return res
    
    # 25/05/2015 (felix) Metodo para registro de pago del bono
    def close_comision(self, cr, uid, ids, context=None):
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

payment_comission_main_itk()


class payment_comission_report_itk(osv.osv):

    _name = 'payment.comission.line'
    _description = 'Campos adicionales para reporte de comisiones'
    
    # 27/05/2015 (felix) Metodo para obtener el porcentaje de comision
    def _get_porcentaje_comision(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        obj_penalization_rule = self.pool.get('penalization.rule')
        all_penalization_rule = obj_penalization_rule.search(cr, uid, [(1, '=', 1)])
        porcentaje_comision = obj_penalization_rule.browse(cr, uid, all_penalization_rule[0], context)['porcentaje_comision']
        for fac in self.browse(cr, uid, ids, context):
            res[fac.id] = float(porcentaje_comision)
        return res
        
    # 27/05/2015 (felix) Metodo para calcular los dias de retraso
    def _calc_dias_retraso(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0
            fecha_act = datetime.now().date()
            fecha_venc = com.due_date
            fecha_pago = com.payment_date
            if fecha_pago:
                if datetime.strptime(fecha_pago, '%Y-%m-%d') > datetime.strptime(fecha_venc, '%Y-%m-%d'):
                    ver = datetime.strptime(fecha_pago, '%Y-%m-%d') - datetime.strptime(fecha_venc, '%Y-%m-%d')
                    res[com.id] = int(str(ver).split(' ')[0])
            else:
                if datetime.strptime(fecha_act, '%Y-%m-%d') > datetime.strptime(fecha_venc, '%Y-%m-%d'):
                    ver = datetime.strptime(fecha_act, '%Y-%m-%d') - datetime.strptime(fecha_venc, '%Y-%m-%d')
                    res[com.id] = int(str(ver).split(' ')[0])
        return res
    
    # 28/05/2015 (felix) Metodo para calculo de porcentaje de penalizacion
    def _get_porcentaje_penalizacion(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        obj_penalizacion_rule = self.pool.get('penalization.rule.line')
        all_penalizacion_rule = obj_penalizacion_rule.search(cr, uid, [(1, '=', 1)])
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            dias_retraso = com.due_days
            for penal in obj_penalizacion_rule.browse(cr, uid, all_penalizacion_rule, context):
                if dias_retraso > penal.qty:
                    res[com.id] = penal.penelization_percent
        return res
        
    # 28/05/2015 (felix) Metodo para calculo de monto de comision
    def _calc_monto_comision(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            utilidad_line = 0.00
            utilidad_porc = 0.00
            for prod_line in com.productos_ids:
                utilidad_line = (prod_line.price_unit * prod_line.quantity) - (prod_line.purchase_price * prod_line.quantity)
                utilidad_porc = (utilidad_line * com.comission_percent) / 100
                res[com.id] += utilidad_porc
        return res
    
    # 28/05/2015 (felix) Metodo para calculo de monto de penalizacion
    def _calc_monto_penalizacion(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            if com.penalization_percent > 0.00:
                res[com.id] = (com.comission * com.penalization_percent) / 100
        return res
        
    # 28/05/2015 (felix) Metodo para calculo de monto de comision con descuento penalizacion
    def _calc_comision_penalizacion(self, cr, uid, ids, fields_name, args, context=None):
        res = {}
        for com in self.browse(cr, uid, ids, context):
            res[com.id] = 0.00
            if com.penalization_amount > 0.00:
                res[com.id] = com.comission - com.penalization_amount
            else:
                res[com.id] = com.comission
        return res
    
    _columns = {
        'comision_id': fields.many2one('payment.comission.main', 'Reporte'),
        'invoice_id': fields.many2one('account.invoice', 'Factura'),
        'fecha_creacion': fields.date('Fecha de creacion'),
        'partner_id': fields.many2one('res.partner', 'Customer Name'),
        'payment_term_id': fields.many2one('account.payment.term', 
            'Invoice Payment Term'),
        'journal_id': fields.many2one('account.journal', 'Account Journal'),
        'due_date': fields.date('Fecha de vencimiento'),
        'invoice_amount': fields.float('Total', 
            digits_compute=dp.get_precision('Account')),
        'payment_date': fields.date('Payment Date'),
        'amount_tax': fields.float('Impuesto', digits=(10,2)),
        'amount_untaxed': fields.float('Subtotal', digits=(10,2)),
        'payment_amount': fields.float('Monto de pago', 
            digits_compute=dp.get_precision('Account')),
        'user_id': fields.many2one('res.users', 'Vendedor'),
        'due_days': fields.function(_calc_dias_retraso, type='integer', 
            string='Dias de retraso'),
        'comission_percent': fields.function(_get_porcentaje_comision, 
            type='float', string='Porcentaje de comision'),
        'penalization_amount': fields.function(_calc_monto_penalizacion, 
            type='float', string='Monto de penalizacion'),
        'penalization_percent': fields.function(_get_porcentaje_penalizacion, 
            type='float', string='Porcentaje de penalizacion'),
        'comission': fields.function(_calc_monto_comision, type='float', 
            string='Monto de comision'),
        'account_move_line_id': fields.many2one('account.move.line', 
            'Journal Item'),
        'state': fields.selection([('open', 'Abierta'), ('paid', 'Pagada'), 
            ('na', 'N/A')], 'Estatus'),
        'comision_penalizacion': fields.function(_calc_comision_penalizacion, 
            type='float', string='Monto comision con descuento pensalizacion'),
        'productos_ids': fields.related('invoice_id', 'invoice_line', 
            type='one2many', relation='account.invoice.line', 
            string='Productos')
    }
    _order = 'invoice_id desc'    

payment_comission_report_itk()

