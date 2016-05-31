# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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
from openerp import api
from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_change_due_date_line(orm.TransientModel):
    _name = 'wizard.change.due.date.line'
    _description = 'Wizard Change Due Date Line'


    def onchange_amount(self,cr, uid, ids, amount=None, context=None):
        list_moveline = self.pool.get('wizard.change.due.date').search(cr, uid, [('move_id', '=', context.get('move_id'))],context=context)
        list2 = self.pool.get('wizard.change.due.date.line').search(cr, uid, [('change_id','=',list_moveline[list_moveline.__len__()-1])], context=context)
        total_new = 0.0
        total_old = 0.0
        for l in list2:
            obj = self.pool.get('wizard.change.due.date.line').browse(cr, uid, l, context=context)
            for o in obj:
                if o.line_state == 'new':
                    total_new += o.amount
                else:
                    total_old += o.amount
        total_new += amount
        diff = total_old-total_new
        return {'value':{'test':diff}}

    def onchange_partner_id(self, cr, uid, ids, partner_id=None, account_id=None, context=None):
        if partner_id:
            list_moveline = self.pool.get('account.move.line').search(cr,uid,[('move_id','=',context.get('move_id')),('date_maturity','!=',None)],context=context)
            account_id = ''
            if list_moveline[0]:
                obj = self.pool.get('account.move.line').browse(cr,uid,list_moveline[0],context=context)

                if obj.account_id.type == 'receivable':
                    account_id = self.pool.get('res.partner').browse(cr, uid, partner_id,context=context).property_account_receivable.id
                elif obj.account_id.type == 'payable':
                    account_id = self.pool.get('res.partner').browse(cr, uid, partner_id,context=context).property_account_payable.id

        return {'value':{'account_id':account_id}}



    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', select=1),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('valid', 'Valid')], 'State'),
        'is_selected': fields.selection([
            ('draft', 'Draft'),
            ('accepted', 'Accepted'),
            ('valid', 'Valid')], 'Selection Type'),
        'account_id': fields.many2one('account.account', 'Account', select=1),
        'change_id': fields.many2one('wizard.change.due.date',
                                         'Change Due Date',
                                         ondelete="cascade",
                                         required=True),
        'line_state': fields.selection([('old', 'Old'),
                                        ('new', 'New'),
                                        ('ref', 'Refused')], 'Line State', default = 'new'),
        'date_original': fields.related('move_line_id', 'date', type='date', relation='account.move.line', string='Original Date', readonly=1),
        'date_due': fields.date('Date Maturity'),
        'payment_type': fields.selection([('C', 'Cash'),
                                                  ('B', 'Bank Transfer'),
                                                  ('D', 'Bank Draft')],
                                                 'Payment Type'),
        'move_line_id': fields.many2one('account.move.line', 'Journal Item'),
        'amount':fields.float('Amount'),
       
        'document_number': fields.related('move_line_id', 'move_id', 'document_number', type='char', relation='account.move', string='Document Number', readonly=1),
    }

