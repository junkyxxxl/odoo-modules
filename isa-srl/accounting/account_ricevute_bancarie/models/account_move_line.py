# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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

from openerp import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def create(self, vals):
        if 'debit' in vals and vals['debit'] < 0:
            vals.update({'credit': vals['debit'], 'debit':0})
        if 'credit' in vals and vals['credit'] < 0:
            vals.update({'debit': -vals['credit'], 'credit':0})
        return super(AccountMoveLine, self).create(vals)

    distinta_line_ids = fields.One2many('riba.distinta.move.line', 'move_line_id', "Dettaglio riba")
    unsolved_invoice_ids = fields.Many2many('account.invoice', 'invoice_unsolved_line_rel', 'line_id', 'invoice_id', 'Unsolved Invoices')
    iban = fields.Char(related='partner_id.bank_ids.iban', string='IBAN', store=False)
    unsolved_move_originator_id = fields.Many2one('account.move', index=True, string='Unsolved Move Originator')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):

        view_payments_tree_id = None
        model_data_obj = self.env['ir.model.data']
        t_ids = model_data_obj.search([
            ('module', '=', 'account_ricevute_bancarie'),
            ('name', '=', 'view_riba_da_emettere_tree')])
        if t_ids:
            view_payments_tree_id = model_data_obj.get_object_reference(
                'account_ricevute_bancarie', 'view_riba_da_emettere_tree')

        if view_payments_tree_id and view_id == view_payments_tree_id[1]:
            return super(models.Model, self).fields_view_get(
                view_id, view_type, toolbar=toolbar, submenu=submenu)
        return super(AccountMoveLine, self).fields_view_get(
            view_id, view_type, toolbar=toolbar, submenu=submenu)
