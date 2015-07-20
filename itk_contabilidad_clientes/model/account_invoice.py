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
from openerp.tools.translate import _

# Python
import logging
_logger = logging.getLogger(__name__)


class account_invoice_line_itk(osv.Model):

    _inherit = 'account.invoice.line'
    _description = 'Datos adicionales para Interkey'
    
    # 12/07/2015 (felix) Metodo para guardar valor de modificacion de precio coste del producto
    def _update_purchase_price(self, cr, uid, ids, name, value, args, context=None):
        cr.execute('SELECT order_line_id FROM sale_order_line_invoice_rel WHERE invoice_id='+str(ids))
        id_order_line = cr.fetchall()
        if id_order_line:
            cr.execute('UPDATE sale_order_line SET purchase_price='+str(value)+' WHERE id='+str(id_order_line[0][0]))
        return True
    
    # 12/07/2015 (felix) Metodo para obtener precio coste del producto
    def _get_purchase_price(self, cr, uid, ids, name_fields, args, context=None):
        res = {}        
        for inv_line in self.browse(cr, uid, ids, context):
            res[inv_line.id] = 0.00
            cr.execute('SELECT order_line_id FROM sale_order_line_invoice_rel WHERE invoice_id='+str(inv_line.id))
            id_order_line = cr.fetchall()
            if id_order_line:
                cr.execute('SELECT purchase_price FROM sale_order_line WHERE id='+str(id_order_line[0][0]))
                purchase_price = cr.fetchall()
                if purchase_price:
                    res[inv_line.id] = purchase_price[0][0]
        return res
    
    _columns = {
        'purchase_price': fields.function(_get_purchase_price, type='float', 
            fnct_inv=_update_purchase_price, string='Precio coste', 
            digits=(10,2))
    }
        
    # 01/07/2015 (felix) Modificacion Metodo original, gregar precio de coste
    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', 
        type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, 
        currency_id=False, context=None, company_id=None):
        
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain':{'uos_id':[]}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain':{'uos_id':[]}}
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        product_uom_obj = self.pool.get('product.uom')
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if type in ('out_invoice','out_refund'):
            a = res.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a

        if type in ('out_invoice', 'out_refund'):
            taxes = res.taxes_id and res.taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        else:
            taxes = res.supplier_taxes_id and res.supplier_taxes_id or (a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False)
        tax_id = fpos_obj.map_tax(cr, uid, fpos, taxes)

        if type in ('in_invoice', 'in_refund'):
            result.update( {'price_unit': price_unit or res.standard_price,'invoice_line_tax_id': tax_id} )
        else:
            result.update({'price_unit': res.list_price, 'invoice_line_tax_id': tax_id})
        result['name'] = res.partner_ref

        result['uos_id'] = res.uom_id.id
        if uom_id:
            uom = product_uom_obj.browse(cr, uid, uom_id)
            if res.uom_id.category_id.id == uom.category_id.id:
                result['uos_id'] = uom_id

        if res.description:
            result['name'] += '\n'+res.description

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            if type in ('in_invoice', 'in_refund'):
                res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
           
        # Precio de coste
        if res:
            res_final['value']['purchase_price'] = res.standard_price
            
        return res_final
    
account_invoice_line_itk()

