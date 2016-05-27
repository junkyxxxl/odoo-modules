# -*- coding: utf-8 -*-
#
# AGPL LICENSE
# ------------
#
# Copyright 2015 Andrea G. <a.gallina@apuliasoftware.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from openerp import models, api, fields
from openerp.tools.translate import _
from math import fabs


class AccountVaucher(models.Model):

    _inherit = 'account.voucher'

    vat_cash_move_id = fields.Many2one('account.move')

    @api.v7
    @api.cr_uid_ids_context
    def action_move_line_create(self, cr, uid, ids, context=None):
        res = super(AccountVaucher, self).action_move_line_create(
            cr, uid, ids, context)
        vat_x_cash_move = self.action_move_line_x_cash(cr, uid, ids, context)
        if vat_x_cash_move:
            self.write(
                cr, uid, ids, {'vat_cash_move_id': vat_x_cash_move}, context)
        return res

    @api.v7
    @api.cr_uid_ids_context
    def action_move_line_x_cash(self, cr, uid, ids, context={}):
        move_obj = self.pool['account.move']
        move_line_obj = self.pool['account.move.line']
        seq_obj = self.pool['ir.sequence']
        fpos_obj = self.pool['account.fiscal.position']
        link_account_obj = self.pool['xcash.link.account']
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        move_id = False
        for voucher in self.browse(cr, uid, ids, context):
            
            ctx = {}
            for item in context.items():
                ctx[item[0]] = item[1]
            ctx['fiscalyear_id'] = voucher.period_id.fiscalyear_id.id  
                      
            for pay_line in voucher.line_ids:
                journal = company.journal_sale_xcash_matured_id
                if pay_line.type == 'dr':
                    journal = company.journal_purch_xcash_matured_id
                if pay_line.amount == 0.0:
                    continue
                if not pay_line.move_line_id.invoice:
                    continue
                invoice = pay_line.move_line_id.invoice
                if not invoice.fiscal_position:
                    continue
                if not invoice.fiscal_position.xcash_vat:
                    continue
                amount_original = pay_line.amount_original
                amount_payed = pay_line.amount
                percent = (amount_payed / amount_original) * 100.0
                vat_x_cash = invoice.amount_tax * percent / 100.0
                name = seq_obj.next_by_id(
                    cr, uid, journal.sequence_id.id, ctx)
                ref = ''
                if invoice.amount_tax_remain:
                    if invoice.number:
                        ref = invoice.number
                    move_id = move_obj.create(
                        cr, uid,
                        {'name': name,
                         'journal_id': journal.id,
                         'narration': 'storno iva x cassa',
                         'date': voucher.date,
                         'ref': ref,
                         'period_id': voucher.period_id.id})

                    # now create the line of move
                    # get the correct value from fiscal position
                    fpos = fpos_obj.browse(cr, uid, invoice.fiscal_position.id,
                                           ctx)
                    accounts = self._get_line_by_value(cr, uid, fpos, invoice,
                                                       vat_x_cash, ctx)
                    # registrazione di un incasso con iva in sospensione
                    if pay_line.type == 'cr':
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa',
                                'debit': vat_x_cash,
                                'partner_id': invoice.partner_id.id,
                                'account_id': accounts['account_id'],
                                'tax_code_id': accounts['tax_code_id'],
                                'tax_amount': vat_x_cash * -1,
                                'move_id': move_id,
                                # 'vat_x_cash_invoice_id': invoice.id,
                                # 'matured_move': True,
                                }, ctx)

                        account_id = link_account_obj._get_related_account(
                            cr, uid, accounts['account_id'], company.id, ctx)
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa',
                                'credit': vat_x_cash,
                                'tax_amount': vat_x_cash,
                                'partner_id': invoice.partner_id.id,
                                'account_id': account_id,
                                'tax_code_id': accounts['rev_tax_code_id'],
                                'move_id': move_id,
                                'vat_x_cash_invoice_id': invoice.id,
                                'matured_move': True,
                                }, ctx)
                    # registrazione di un pagamento con iva in sospensione
                    if pay_line.type == 'dr':
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa',
                                'credit': vat_x_cash,
                                'tax_amount': vat_x_cash ,
                                'partner_id': invoice.partner_id.id,
                                'account_id': accounts['account_id'],
                                'tax_code_id': accounts['tax_code_id'],
                                'move_id': move_id,
                                # 'vat_x_cash_invoice_id': invoice.id,
                                # 'matured_move': True,
                                }, ctx)

                        account_id = link_account_obj._get_related_account(
                            cr, uid, accounts['account_id'], company.id, ctx)
                        move_line_obj.create(
                            cr, uid, {
                                'name': 'storno iva x cassa',
                                'debit': vat_x_cash ,
                                'tax_amount': vat_x_cash * -1,
                                'partner_id': invoice.partner_id.id,
                                'account_id': account_id,
                                'tax_code_id': accounts['rev_tax_code_id'],
                                'move_id': move_id,
                                'vat_x_cash_invoice_id': invoice.id,
                                'matured_move': True,
                                }, ctx)

                # now validate the move
                if move_id:
                    move_obj.post(cr, uid, [move_id], ctx)
        return move_id

    @api.v7
    @api.cr_uid_ids_context
    def _get_line_by_value(self, cr, uid, fpos, invoice, amount, context={}):
        if not invoice or not amount or not fpos:
            return False
        res = {}
        for tax_line in invoice.tax_line:
            if amount <= fabs(tax_line.tax_amount):
                rev_tax_code_id = tax_line.tax_code_id.xcash_tax_code.id
                res = {'account_id': tax_line.account_id.id,
                       'tax_code_id': tax_line.tax_code_id.id,
                       'rev_tax_code_id': rev_tax_code_id}
            else:
                continue
        if not res:
            raise Warning(_('Importo del pagamento errato!'))
        return res

    @api.v7
    @api.cr_uid_ids_context
    def cancel_voucher(self, cr, uid, ids, context=None):
        res = super(AccountVaucher, self).cancel_voucher(cr, uid, ids, context)
        move_obj = self.pool['account.move']
        for voucher in self.browse(cr, uid, ids, context):
            if voucher.vat_cash_move_id:
                move_obj.button_cancel(cr, uid, [voucher.vat_cash_move_id.id])
                move_obj.unlink(cr, uid, [voucher.vat_cash_move_id.id])
        return res
