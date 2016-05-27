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
from openerp import api


class wizard_change_due_date(orm.TransientModel):
    _name = 'wizard.change.due.date'
    _description = 'Wizard Change Due Date'
    
    def _get_amount_to_complete(self, cr, uid, ids, field_name,
                               arg, context=None):
        res = {}
        t_amount_old = 0.0
        t_amount_new = 0.0
        for rec in self.browse(cr, uid, ids):
            t_amount_old = 0.0
            t_amount_new = 0.0
            for t_line in rec.old_ids:
                t_amount_old += t_line.amount
            
            for t_line in rec.new_ids:
                t_amount_new += t_line.amount
            
            res[rec.id] = t_amount_old - t_amount_new
        return res
   
    _columns = {
        'move_id': fields.many2one('account.move',
                                   'Move'),
        'invoice_id': fields.many2one('account.invoice',
                                   'Invoice'),
        'partner_id': fields.related('move_id',
                                     'partner_id',
                                     type='many2one',
                                     relation='res.partner',
                                     string='Partner'),
        'old_ids': fields.one2many(
                              'wizard.change.due.date.line',
                              'change_id',
                              domain=[('line_state', '=', 'old')],
                              string="Originals",
                              readonly=True),
        'new_ids': fields.one2many(
                              'wizard.change.due.date.line',
                              'change_id',
                              domain=[('line_state','=','new')],
                              readonly=False,
                              string="New Move Line",),
        'amount_to_complete': fields.function(
                                              _get_amount_to_complete,
                                              string="Amount To Add",
                                              type="float"
                                            ),
    }
    
    def add_new_line(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_voucher_makeover',
                                              'wizard_add_new_line_view')
        
        context.update({
            'default_change_id': ids[0]
        })
        view_id = result and result[1] or False

        return {
              'name': _("Add New Line"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.add.new.line',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new',
              }
        
    def change_move(self, cr, uid, ids, context=None):
        print 'ok'
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        bank_draft_rel_obj = self.pool.get('account.move.bank.draft.rel')
        
        t_wizard = self.browse(cr, uid, ids[0])
        t_invoice = t_wizard.invoice_id
        t_move = t_wizard.move_id
        t_debit_flag = 0.0
        t_credit_flag = 0.0
        t_amount_old = 0.0
        t_amount_new = 0.0
        t_amount = 0.0
        
        if(t_invoice.type == 'in_invoice' or t_invoice.type == 'out_refund'):
            t_credit_flag = 1.0
        else:
            t_debit_flag = 1.0
            #somma tutte le old line che trova nella tabella wizard_change_due_date_line
        for t_line in t_wizard.old_ids:
            t_amount_old += t_line.amount
            #somma tutte le new line che trova nella tabella wizard_canghe_due_date_line
        for t_line in t_wizard.new_ids:
            t_amount_new += t_line.amount
        
        if(str(t_amount_old) != str(t_amount_new)):
            #print abs(t_amount_old - t_amount_new) aggiungere un controllo preciso sulle date
            raise orm.except_orm(_('Attenzione!'),
                                 _("L'importo totale delle nuove scandenze deve coincidere con l'originale"))
        
        
        t_lines = []
        for t_line in t_wizard.old_ids:
             id=t_line.move_line_id.id
             
            #Rimuovo le vecchie move_line_id
            
             cr.execute('DELETE '\
                    'FROM account_move_line '\
                    'WHERE id=%s ', (id,))
             
             
        #le aggiungo alla tabella account_move_line      
        t_lines = []
        for t_line in t_wizard.new_ids:
             if not t_invoice and t_line.amount < 0:
                 t_debit_flag = 0.0
                 t_credit_flag = -1.0
                 
             t_lines.append((0, 0, {
                                        'partner_id': t_line.partner_id.id,
                                        'account_id': t_line.account_id.id,
                                        'debit': t_line.amount * t_debit_flag,
                                        'credit': t_line.amount * t_credit_flag,
                                        'date_maturity': t_line.date_due,
                                        'payment_type_move_line': t_line.payment_type,
                                        'state': 'valid',
                                        'amount_to_pay': -t_line.amount, 
                                        'received_check': "f",
                                        'day': t_line.date_due,
                                        'name': "/"
                                }))
             
             
        move_obj.write(cr, uid, [t_move.id], {
                                           'line_id': t_lines
                                           })
         
                
        return t_move.id


    
    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
       
        res_id = self.change_move(cr, uid, ids)
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account',
                                              'view_move_form')
        view_id = result and result[1] or False

        return {
              'name': _("Add New Line"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'account.move',
              'type': 'ir.actions.act_window',
              'res_id': res_id,
              'view_id': view_id,
              'context': context,
              'target': 'current',
              }
