# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp import api


class account_invoice_line_montecristo(osv.osv):

    _inherit = "account.invoice.line"

    def _commission_base(self, cr, uid, ids, name, arg, context=None):
        res = {}
        salesagent_common_obj = self.pool.get('salesagent.common')
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {'commission_base':0.0, 'commission_percentage_base':0.0, 'commission':0.0, 'commission_percentage':0.0,}
            if not line.no_commission:
                if line.invoice_id.type == 'out_invoice':
                    sign = 1
                elif line.invoice_id.type == 'out_refund':
                    sign = -1
                else:
                    sign = 0                
                # ----- if a paid commission exist, show it or calculate it
                if line.paid_commission_value:
                    comm = line.paid_commission_value
                    comm_percentage = line.paid_commission_percentage_value
                else:
                    comm = sign * salesagent_common_obj.commission_calculate(cr, uid, 'account.invoice.line', line.id, base=False)
                    comm_percentage = salesagent_common_obj.recognized_commission(cr, uid, line.partner_id and [line.partner_id.id] or False, line.salesagent_id and [line.salesagent_id.id] or False, line.product_id and line.product_id.id or False, base=False)

                
                if line.paid_commission_value_base:
                    comm_base = line.paid_commission_value_base
                    comm_percentage_base = line.paid_commission_percentage_value_base
                else:
                    comm_base = sign * salesagent_common_obj.commission_calculate(cr, uid, 'account.invoice.line', line.id, base=True)
                    comm_percentage_base = salesagent_common_obj.recognized_commission(cr, uid, line.partner_id and [line.partner_id.id] or False, line.salesagent_id and [line.salesagent_id.id] or False, line.product_id and line.product_id.id or False, base=True)
                res[line.id]['commission'] = comm
                res[line.id]['commission_percentage'] = comm_percentage   
                res[line.id]['commission_base'] = comm_base
                res[line.id]['commission_percentage_base'] = comm_percentage_base

        return res

    def _comm_presence(self, cr, uid, ids, name, arg, context=None):
        res = {}
        salesagent_common_obj = self.pool.get('salesagent.common')
        for line in self.browse(cr, uid, ids, context=context):
            if not line.no_commission:
                if line.commission != 0 or line.commission_base != 0:
                    res[line.id] = True
                else:
                    res[line.id] = False
            else:
                res[line.id] = False
        return res 

    def _paid_commission(self, cr, uid, ids, name, arg, context=None):
        res = {}
        salesagent_common_obj = self.pool.get('salesagent.common')
        for line in self.browse(cr, uid, ids, context=context):
            if not line.no_commission:
                if line.commission != 0 or line.commission_base != 0:
                    if line.commission == 0:                 
                        res[line.id] = True
                    elif line.commission == line.paid_commission_value:
                        res[line.id] = True
                    else:
                        res[line.id] = False
                else:
                    res[line.id] = False
            else:
                res[line.id] = True
        return res 

    def _paid_commission_base(self, cr, uid, ids, name, arg, context=None):
        res = {}
        salesagent_common_obj = self.pool.get('salesagent.common')
        for line in self.browse(cr, uid, ids, context=context):
            if not line.no_commission:
                if line.commission != 0 or line.commission_base != 0:
                    if line.commission_base == 0:                 
                        res[line.id] = True
                    elif line.commission == line.paid_commission_value_base:
                        res[line.id] = True                        
                    else:
                        res[line.id] = False
                else:
                    res[line.id] = False
            else:
                res[line.id] = False
        return res 
        
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        res = super(account_invoice_line_montecristo,self).product_id_change(product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, company_id=company_id)
        if product:
            res['value']['no_commission'] = self.pool.get('product.product').browse(self._cr, self._uid, product).no_commission
        else:
            res['value']['no_commission'] = True
        return res

    def _get_lines(self, cr, uid, ids, context=None):
        result = {}
        for invoice in self.pool.get('account.invoice').browse(cr, uid, ids, context=context):
            for line in invoice.invoice_line:
                result[line.id] = True
        return result.keys()

    _columns = {
        'commission_percentage' : fields.function(_commission_base, string='Comm. Percentage', type='float', multi='comm',
                store={
                       'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','paid_commission_value_base','paid_commission_percentage_value_base','partner_id','salesagent_id','product_id'], 10),                       
                       'account.invoice': (_get_lines, ['partner_id','salesagent_id','type'], 20),
                        }),
        'commission' : fields.function(_commission_base, string='Provv. Total', type='float', multi='comm',
                store={
                       'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','paid_commission_value_base','paid_commission_percentage_value_base','partner_id','salesagent_id','product_id'], 10),                       
                       'account.invoice': (_get_lines, ['partner_id','salesagent_id','type','global_discount_lines'], 20),
                        }),               
        'commission_percentage_base' : fields.function(_commission_base, string='Comm. Percentage Base', type='float', multi='comm',
                store={
                       'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','paid_commission_value_base','paid_commission_percentage_value_base','partner_id','salesagent_id','product_id'], 10),                       
                       'account.invoice': (_get_lines, ['partner_id','salesagent_id','type'], 20),
                        }),
        'commission_base' : fields.function(_commission_base, string='Provv. Total Base', type='float', multi='comm',
                store={
                       'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','paid_commission_value_base','paid_commission_percentage_value_base','partner_id','salesagent_id','product_id'], 10),                       
                       'account.invoice': (_get_lines, ['partner_id','salesagent_id','type','global_discount_lines'], 20),
                        }),
        'paid_commission_base' : fields.function(_paid_commission_base, string='Paid', type='boolean', 
                 store={
                        'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','commission','commission_base','paid_commission_value_base'], 10)
                        }),
        'paid_commission' : fields.function(_paid_commission, string='Paid', type='boolean', 
                 store={
                        'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','commission','commission_base','paid_commission_value'], 10)
                        }),        
        'commission_presence' : fields.function(_comm_presence, string='Commission Presence', type='boolean', 
                 store={
                        'account.invoice.line': (lambda self, cr, uid, ids, c={}: ids, ['no_commission','commission','commission_base'], 20)
                        }),                
        'salesagent_id' : fields.related('invoice_id', 'salesagent_id', type='many2one', relation='res.partner', string='Salesagent', store=True),        
        'salesagent_id_base' : fields.related('partner_id', 'salesagent_for_customer_id', type='many2one', relation='res.partner', string='Salesagent Base', store=True),
        'paid_commission_value_base' : fields.float('Paid Commission Base'),
        'paid_commission_percentage_value_base' : fields.float('Paid Commission Percentage Base'),
        'payment_commission_date_base' : fields.date('Payment Commission Base Date'),
        'payment_commission_note_base' : fields.char('Payment Commission Base Note', size=128), 
    }

    _defaults = {
         'payment_commission_date_base': None,
         'payment_commission_note_base': None,                   
         'paid_commission_value_base' : 0.0,
        }
