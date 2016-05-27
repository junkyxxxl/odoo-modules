# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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


class custom_sale_order(osv.osv):
    _inherit = "sale.order"

    def _compute_part_payment_amount(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for item in self.browse(cr, uid, ids, context=context):
            if item.part_payment == 0 or item.amount_total == 0:
                result[item.id] = 0.0
            else:
                result[item.id] = item.amount_total*item.part_payment/100
        return result

    _columns = {
                'part_payment': fields.float(string='Acconto [%]'),
                'part_payment_amount':fields.function(_compute_part_payment_amount, type='float', stored=True, string='Totale acconto'),
    }

    def manual_invoice(self, cr, uid, ids, context=None):
        res = super(custom_sale_order, self).manual_invoice(cr, uid, ids, context=context)
        inv_obj = self.pool.get('account.invoice')
        if res.get('res_id', False):
            if isinstance(res['res_id'], list):
                res_ids = res['res_id']
            else:
                res_ids = [res['res_id']]
            vals = {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}            
            if context.get('wiz_journal_id', False):
                for id in res_ids:
                    vals.update({'journal_id':context['wiz_journal_id']})
            inv_obj.write(cr, uid, id, vals, context=context)
        return res
