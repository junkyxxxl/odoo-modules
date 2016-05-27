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


class wizard_payment_wht_specification_line(orm.TransientModel):
    _name = 'wizard.payment.wht.specification.line'
    _description = 'Wizard Payment Wht Specification Line'
    

    _columns = {
        'state': fields.selection([
            ('confirmed', 'Confirmed'),
            ('selected', 'Selected')], 'State'),
        'move_line_id': fields.many2one('account.move.line', 'Move Line'),
        'account_id': fields.many2one('account.account', 'Account'),
        'partner_id': fields.many2one('res.partner', 'Supplier'),
        'payment_specification_id': fields.many2one('wizard.payment.wht.specification',
                                         'Payment Specification',
                                         ondelete="cascade",
                                         required=True),
        'amount': fields.float('Amount')
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

    
    def set_payment_lines(self, cr, uid, context=None):

        t_lines = []
        t_limit = 50
        t_page = context.get('default_actual_page', None)
        wizard_obj = self.pool.get('wizard.payment.wht.specification')
        wizard_wht_obj = self.pool.get('wizard.payment.wht')
        account_move_line_obj = self.pool.get('account.move.line')
       
        t_filters = self.get_wizard_confirmed_filters(context)
        
        t_total_pages = wizard_wht_obj.get_total_pages(cr, uid, t_filters, t_limit)
        
        if(t_page > t_total_pages or t_total_pages == 1):
            t_page = t_total_pages
            context.update({
                            'default_actual_page': t_page,
                           })
        
        t_offset = t_limit * (t_page - 1)
        
        res_id = wizard_obj.create(cr, uid, {
                                             'total_pages': t_total_pages,
                                             }, context)
        
        account_move_line_ids = account_move_line_obj.search(cr, uid, t_filters,
                                                             order='id',
                                                             limit=t_limit,
                                                             offset=t_offset,
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
   
    
    
    def move_draft_forward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(1, cr, uid, ids, context)

    def move_draft_backward(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return self.move_draft(0, cr, uid, ids, context)
    
    def move_draft(self, fb, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_id = context.get('line_id', None)
        data = self.browse(cr, uid, line_id, context=context)
        t_journal = data.payment_specification_id.journal_id.id
        t_maturity = data.payment_specification_id.maturity
        t_page = data.payment_specification_id.actual_page
        
        t_state = 'confirmed'
        if fb:
            t_state = 'selected'
            
        draft_obj = self.pool.get('account.move.line')
        t_move_id = data.move_line_id.id
        draft_obj.write(cr, uid, [t_move_id], {
            'wht_state': t_state,
        })
#        t_move = data.move_line_id.move_id
        
        context.update({
            'default_journal_id': t_journal,
            'default_maturity': t_maturity,
            'default_actual_page': t_page,
        })
        
        res_id = self.set_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_wht_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Wht Payment Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.wht.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

   

