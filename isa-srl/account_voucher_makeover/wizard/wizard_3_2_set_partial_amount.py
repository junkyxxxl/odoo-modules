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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_set_partial_amount(orm.TransientModel):
    _name = 'wizard.set.partial.amount'
    _description = 'Wizard Set Partial Amount'

    _columns = {
              'line_id': fields.many2one('wizard.confirm.payment.line',
                                         'Line'),
              'partner_id': fields.many2one('res.partner', 'Supplier'),
              'amount_partial': fields.float('Amount Partial'),
              'amount_initial': fields.float('Amount Initial'),
              'amount_residual': fields.float('Amount Residual'),
              'allowance': fields.boolean('allowance'),
              'partner_bank_id': fields.many2one('res.partner.bank',
                                           'Partner Bank'),
              'payment_type': fields.selection([('C', 'Cash'),
                                                  ('B', 'Bank Transfer'),
                                                  ('D', 'Bank Draft')],
                                                 'Payment Type'),
    }
    
    def onchange_amount_partial(self, cr, uid, ids, amount_initial, amount_partial, context=None):
        t_residual = amount_initial - amount_partial
        
        return {'value': {
                          'amount_partial': amount_partial,
                          'amount_residual': t_residual,
                          'amount_initial': amount_initial,
                    }
        }
    
    def confirm(self, cr, uid, ids, context=None):
       
        form = self.read(cr, uid, ids)[0]
        t_partner_bank_id = None
        if(form["line_id"]):
            t_line_id = form["line_id"][0]
        t_amount_partial = form["amount_partial"]
        t_allowance = form['allowance']
        t_allowance_residual = form["amount_initial"] - form["amount_partial"]
        t_payment_type = form["payment_type"]
        if(form["partner_bank_id"]):
            t_partner_bank_id = form["partner_bank_id"][0]
            
        t_obj = self.pool.get('wizard.confirm.payment.line')
        t_amount = t_obj.browse(cr, uid, t_line_id).amount
        t_1 = int(t_amount / 10)
        t_2 = t_1 * 10
        t_check_value = t_2 + 10
        t_check_value_2 = t_2 - 10
        if(t_amount_partial <= 0.0):
            raise orm.except_orm(_('Error!'), _('Inserire un importo positivo e non nullo'))
        if(not t_allowance and t_amount < t_amount_partial):
            raise orm.except_orm(_('Error!'), _('Inserire importo inferiore di ' + str(t_amount)))
        if(t_check_value < t_amount_partial and t_allowance):
            raise orm.except_orm(_('Error!'), _('Per allowance passivo inserire importo inferiore di ' + str(t_check_value)))
        if(t_check_value_2 > t_amount_partial and t_allowance):
            raise orm.except_orm(_('Error!'), _('Per allowance attivo inserire importo maggiore di ' + str(t_check_value_2)))
        res = t_obj.write(cr, uid, [t_line_id], {'amount_partial': t_amount_partial,
                                                 'amount_allowance': t_allowance_residual,
                                                 'allowance': t_allowance,
                                                 'payment_type': t_payment_type,
                                                 'partner_bank_id': t_partner_bank_id})
        
        return res
