##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

# Python
import logging
_logger = logging.getLogger(__name__)

class sale_advance_payment_inv_itk_1(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"
    
    _logger.warn('Pasa por aqui')

    def _create_invoices(self, cr, uid, inv_values, sale_id, context=None):
        result = super(sale_advance_payment_inv, self)._create_invoices(cr, uid, inv_values, sale_id, context=context)
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        wizard = self.browse(cr, uid, [result], context)
        sale = sale_obj.browse(cr, uid, sale_id, context=context)

        # If invoice on picking: add the cost on the SO
        # If not, the advance will be deduced when generating the final invoice
        line_name = inv_values.get('invoice_line') and inv_values.get('invoice_line')[0][2].get('name') or ''
        line_tax = inv_values.get('invoice_line') and inv_values.get('invoice_line')[0][2].get('invoice_line_tax_id') or False
        purchase_price = inv_values.get('invoice_line') and inv_values.get('invoice_line')[0][2].get('purchase_price') or 0.00
        if sale.order_policy == 'picking':
            vals = {
                'order_id': sale.id,
                'name': line_name,
                'price_unit': -inv_amount,
                'product_uom_qty': wizard.qtty or 1.0,
                'product_uos_qty': wizard.qtty or 1.0,
                'product_uos': res.get('uos_id', False),
                'product_uom': res.get('uom_id', False),
                'product_id': wizard.product_id.id or False,
                'discount': False,
                'tax_id': line_tax,
                'purchase_price': purchase_price
            }
            sale_line_obj.create(cr, uid, vals, context=context)
        return result

sale_advance_payment_inv_itk_1()
