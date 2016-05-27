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

class account_invoice_montecristo(osv.osv):

    _inherit = "account.invoice"

    def _total_commission_base(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            sign = 1
            total_commission = 0.0 
            for line in invoice.invoice_line:
                total_commission += (line.commission_base * sign)
            res[invoice.id] = total_commission
        return res

    def _total_commission_agent(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            sign = 1
            total_commission = 0.0 
            for line in invoice.invoice_line:
                total_commission += (line.commission * sign)
            res[invoice.id] = total_commission
        return res

    def _total_commission(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            sign = 1
            total_commission = 0.0 
            for line in invoice.invoice_line:
                total_commission += (line.commission * sign) + (line.commission_base * sign)
            res[invoice.id] = total_commission
        return res

    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False, context=None):
            
            return super(account_invoice_montecristo, self).onchange_partner_id(cr, uid, ids, type, partner_id,
                                                                                date_invoice, payment_term,
                                                                                partner_bank_id, company_id)

    def _get_commission(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            if line.invoice_id:
                result[line.invoice_id.id] = True
        return result.keys()

    _columns = {
        'commission' : fields.function(_total_commission,
                                       method=True,
                                       string='Commission',
                                       type='float',
                                       store={
                                              'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['partner_id','salesagent_id','type','invoice_line','global_discount_lines'], 30),
                                              'account.invoice.line': (_get_commission, ['no_commission','paid_commission_value_base','paid_commission_percentage_value_base','partner_id','salesagent_id','product_id'], 25),
                                              }),
    }
