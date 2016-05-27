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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class wizard_payment_wht(orm.TransientModel):
    _name = 'wizard.payment.wht'
    _description = 'Wizard Payment Wht'
    
    _columns = {
        'maturity': fields.date('Maturity Maximum'),
    }

    def get_wizard_confirmed_filters(self, context=None):
        filters = []
        t_maturity = context.get('default_maturity', None)
        if(t_maturity):           
            f = ('date_maturity', '<=', t_maturity)
            filters.append(f)
        filters.append(('wht_state', '=', 'confirmed'))
        if(len(filters) > 1):
            filters.insert(0, '&')
        return filters

    def get_wizard_selected_filters(self, context=None):
        filters = []
        t_maturity = context.get('default_maturity', None)
        if(t_maturity):           
            f = ('date_maturity', '<=', t_maturity)
            filters.append(f)
        filters.append(('wht_state', '=', 'selected'))
        if(len(filters) > 1):
            filters.insert(0, '&')
        return filters

    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        form = self.read(cr, uid, ids)[0]    
        t_maturity = form["maturity"]
        context.update({
            'default_journal_id': self.pool.get('account.voucher')._get_journal(cr, uid),
            'default_maturity': t_maturity,
        })

        res_id = self.set_payment_lines(cr, uid, context)
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_wht_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Payment Wht Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.wht.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview'
              }
        
    def get_total_pages(self, cr, uid, v_filters, t_limit):
        move_line_obj = self.pool.get('account.move.line')
        valid_all_ids = move_line_obj.search(cr, uid,
                                             v_filters, 
                                             order='date_maturity, id')
        t_total_pages = 1
        if valid_all_ids:
            t_total_pages = int(len(valid_all_ids) / t_limit)
            if (len(valid_all_ids) % t_limit) > 0:
                t_total_pages += 1
        return t_total_pages
    
    def set_payment_lines(self, cr, uid, context=None):

        t_lines = []
        t_limit = 50
        wizard_obj = self.pool.get('wizard.payment.wht.specification')
        account_move_line_obj = self.pool.get('account.move.line')

        t_filters = self.get_wizard_confirmed_filters(context)
        
        t_total_pages = self.get_total_pages(cr, uid, t_filters, t_limit)
        
        res_id = wizard_obj.create(cr, uid, {
                                             'total_pages': t_total_pages
                                             }, context)
        
        account_move_line_ids = account_move_line_obj.search(cr, uid, t_filters,
                                                             order='id',
                                                             limit=t_limit,
                                                             offset=0,
                                                             context=context)
                
        for line in account_move_line_obj.browse(cr, uid, account_move_line_ids):
                            t_move_line_id = line.id
                            t_state = line.wht_state
                            t_lines.append((0, 0, {
                                                   'state': t_state,
                                                   'move_line_id': t_move_line_id,
                                                   'partner_id': line.partner_id.id,
                                                   'account_id': line.account_id.id,
                                                   'payment_specification_id': res_id,
                                                   'amount': line.credit
                                                   }))
       
        self.pool.get('wizard.payment.wht.specification').write(cr, uid, [res_id], {'confirmed_ids': t_lines, })
            
        t_lines = []
        t_filters = []
        t_filters = self.get_wizard_selected_filters(context)
        account_move_line_ids = []
        account_move_line_ids = account_move_line_obj.search(cr, uid, t_filters,
                                                             order='id',
                                                             context=context)
        
        for line in account_move_line_obj.browse(cr, uid, account_move_line_ids):
                            t_move_line_id = line.id
                            t_state = line.wht_state
                            t_lines.append((0, 0, {
                                                   'state': t_state,
                                                   'move_line_id': t_move_line_id,
                                                   'partner_id': line.partner_id.id,
                                                   'account_id': line.account_id.id,
                                                   'payment_specification_id': res_id,
                                                   'amount': line.credit
                                                   }))
       
        self.pool.get('wizard.payment.wht.specification').write(cr, uid, [res_id], {'selected_ids': t_lines, })
  
        return res_id
