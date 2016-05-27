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


class wizard_payment_wht_specification(orm.TransientModel):
    _name = 'wizard.payment.wht.specification'
    _description = 'Wizard Payment Wht Specification'
    
    def _resume_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = str(t_wizard.actual_page)
            t_total = str(t_wizard.total_pages)
            res[t_wizard.id] = t_actual + ' di ' + t_total
        return res
    
    def _is_last_page(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for t_wizard in self.browse(cr, uid, ids, context):
            t_actual = t_wizard.actual_page
            t_total = t_wizard.total_pages
            if t_actual == t_total:
                res[t_wizard.id] = True
            else:
                res[t_wizard.id] = False
        return res
    
    _columns = {
        'journal_id':fields.many2one('account.journal', 'Journal'),
        'maturity': fields.date('Maturity Maximum'),
        'confirmed_ids': fields.one2many(
                              'wizard.payment.wht.specification.line',
                              'payment_specification_id',
                              domain=[('state', '=', 'confirmed')],
                              string="Open",
                              readonly=True),
        'selected_ids': fields.one2many(
                              'wizard.payment.wht.specification.line',
                              'payment_specification_id',
                              domain=[('state', '=', 'selected')],
                              string="Selected",
                              readonly=True),
        'actual_page': fields.integer('Actual Page'),
        'total_pages': fields.integer('Total Pages'),
        'pages_resume': fields.function(_resume_page,
                                  string='Page',
                                  type='text'),
        'is_last_page': fields.function(_is_last_page,
                                  string='Is Last Page',
                                  type='boolean'),
    }
    
    _defaults = {
                 'actual_page': 1
                 }

    def view_new_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_wht_view')
        view_id = result and result[1] or False

        return {
              'name': _("Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.wht',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }   

    def set_confirm_payment_lines(self, cr, uid, ids, context=None):

        t_lines = []
        vals = {}
        t_maturity = context.get('default_maturity', None)
        vals['maturity'] = t_maturity
        vals['company_id'] = self.pool.get('res.users')._get_company(cr, uid, context=context)
        res_id = self.pool.get('wizard.confirm.payment.wht').create(cr, uid, vals, context=context)
        
        t_wps = self.browse(cr, uid, ids[0])
        
        for line in t_wps.selected_ids:
            t_move_line = line['move_line_id']
            t_state = t_move_line.wht_state
            t_lines.append((0, 0, {
                                   'state': t_state,
                                   'is_selected': 'accepted',
                                   'move_line_id': t_move_line.id,
                                   'partner_id': t_move_line.partner_id.id,
                                   'account_id': t_move_line.account_id.id,
                                   'confirm_payment_wht_id': res_id,
                                   'amount': line.amount,
                                   }))
            
        self.pool.get('wizard.confirm.payment.wht').write(cr, uid, [res_id], {'line_ids': t_lines})
              
        return res_id
    
    def view_confirm_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_confirm_payment_wht_view')
        view_id = result and result[1] or False
        
        t_ws = self.browse(cr, uid, ids[0])
        if(not t_ws.selected_ids and len(t_ws.selected_ids) < 1):
            raise orm.except_orm(_('Error!'), _('Selezionare almeno una riga se presente'))
        
        res_id = self.set_confirm_payment_lines(cr, uid, ids, context)
        
        return {
              'name': _("Confirm Payment Action"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.confirm.payment.wht',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview'
              }
          
    def action_move_all_forward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.payment.wht.specification.line')
        for line in t_spec.confirmed_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_forward(cr, uid, ids, context=context)
        return res
    
    def action_move_all_backward(self, cr, uid, ids, context=None):
        res = None
        t_spec = self.browse(cr, uid, ids[0])
        line_obj = self.pool.get('wizard.payment.wht.specification.line')
        for line in t_spec.selected_ids:
            context.update({
                            'line_id': line.id
                            })
            res = line_obj.move_draft_backward(cr, uid, ids, context=context)
        return res
    
    def move_page(self, cr, uid, ids, context=None):
        wizard_line_obj = self.pool.get('wizard.payment.wht.specification.line')
        data = self.browse(cr, uid, ids[0], context=context)
        
        t_maturity = data.maturity
        t_journal = data.journal_id.id
        t_total_pages = data.total_pages
        
        t_skip = context.get('t_skip', None)
        if(data.actual_page == 1 and t_skip == -1):
            raise orm.except_orm(_('Error!'), _('Non puoi andare indietro!'))
            
        if(data.actual_page >= t_total_pages and t_skip == 1):
            raise orm.except_orm(_('Error!'), _("Hai raggiunto l'ultima pagina!"))

        t_page = data.actual_page + t_skip
        
        context.update({
            'default_journal_id': t_journal,
            'default_maturity': t_maturity,
            'default_actual_page': t_page,
            'default_total_pages': t_total_pages
        })

        res_id = wizard_line_obj.set_payment_lines(cr, uid, context)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_payment_wht_specification_view')
        view_id = result and result[1] or False

        return {
              'name': _("Wizard Payment Specification"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.payment.wht.specification',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'inlineview',
              }

        
