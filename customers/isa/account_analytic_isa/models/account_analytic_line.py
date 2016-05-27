# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import osv


class AccountAnalyticLine(osv.osv):
    _inherit = 'account.analytic.line'

    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        analytic_line_obj = self.pool.get('account.analytic.line')
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        # use key (partner/account, company, currency)
        # creates one invoice per key
        invoice_grouping = {}

        currency_id = False
        # prepare for iteration on journal and accounts
        for line in self.browse(cr, uid, ids, context=context):

            # raggruppa i ticket
            t_id = line.account_id.id
            if line.account_id.name[:3] == 'HB_':
                t_id = 'HB'
            t_partner = line.account_id.partner_id.id
            if line.account_id.partner_id.parent_id:
                t_partner = line.account_id.partner_id.parent_id.id

            key = (t_id,
                   t_partner,
                   line.account_id.company_id.id,
                   line.account_id.pricelist_id.currency_id.id)
            invoice_grouping.setdefault(key, []).append(line)

        for (key_id, partner_id, company_id, currency_id), analytic_lines in invoice_grouping.items():
            # key_id is an account.analytic.account
            account = analytic_lines[0].account_id
            partner = account.partner_id  # will be the same for every line

            # per gestire il caso in cui nel campo Cliente ci sia un contatto
            if partner.parent_id:
                partner = partner.parent_id

            if (not partner) or not (currency_id):
                raise osv.except_osv(_('Error!'), _('Contract incomplete. Please fill in the Customer and Pricelist fields for %s.') % (account.name))

            curr_invoice = self._prepare_cost_invoice(cr, uid, partner, company_id, currency_id, analytic_lines, context=context)
            invoice_context = dict(context,
                                   lang=partner.lang,
                                   force_company=company_id,  # set force_company in context so the correct product properties are selected (eg. income account)
                                   company_id=company_id)  # set company_id in context, so the correct default journal will be selected
            last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=invoice_context)
            invoices.append(last_invoice)

            # use key (product, uom, user, invoiceable, analytic account, journal type)
            # creates one invoice line per key
            invoice_lines_grouping = {}
            for analytic_line in analytic_lines:
                account = analytic_line.account_id

                if not analytic_line.to_invoice:
                    raise osv.except_osv(_('Error!'), _('Trying to invoice non invoiceable line for %s.') % (analytic_line.product_id.name))

                t_user_id = -1

                key = (analytic_line.product_id.id,
                       analytic_line.product_uom_id.id,
                       t_user_id,
                       analytic_line.to_invoice.id,
                       analytic_line.account_id,
                       analytic_line.journal_id.type)
                # We want to retrieve the data in the partner language for the invoice creation
                analytic_line = analytic_line_obj.browse(cr, uid, [line.id for line in analytic_line], context=invoice_context)
                invoice_lines_grouping.setdefault(key, []).append(analytic_line)

            # finally creates the invoice line
            for (product_id, uom, user_id, factor_id, account, journal_type), lines_to_invoice in invoice_lines_grouping.items():
                curr_invoice_line = self._prepare_cost_invoice_line(cr, uid, last_invoice,
                    product_id, uom, user_id, factor_id, account, lines_to_invoice,
                    journal_type, data, context=invoice_context)

                invoice_line_obj.create(cr, uid, curr_invoice_line, context=context)
            self.write(cr, uid, [l.id for l in analytic_lines], {'invoice_id': last_invoice}, context=context)
            invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices

    def _prepare_cost_invoice_line(self, cr, uid, invoice_id, product_id, uom, user_id,
                                   factor_id, account, analytic_lines, journal_type, data, context=None):
        if context is None:
            context = {}
        res = super(AccountAnalyticLine, self)._prepare_cost_invoice_line(
            cr, uid, invoice_id, product_id, uom, user_id,
            factor_id, account, analytic_lines, journal_type, data, context)

        if account.name[:3] == 'HB_':
            area_name = ''
            for tag in account.area_hb_ids:
                if area_name:
                    area_name += ', '
                area_name += tag.name
            partner_obj = self.pool.get('res.partner')
            project_obj = self.pool.get('project.project')
            partner_name = partner_obj.name_get(cr, uid, account.partner_id.id, context=context)[0][1]
            line_name = 'Ticket "' + account.name + \
                        '" del ' + account.date_start + ', effettuato da ' + partner_name
            if area_name:
                line_name += ' - Area ' + area_name
            project_ids = project_obj.search(cr, uid, [('analytic_account_id', '=', account.id)], limit=1)
            if project_ids:
                project_data = project_obj.browse(cr, uid, project_ids[0], context=context)
                if project_data.closing_category_id:
                    closing_category = project_data.closing_category_id.name
                    line_name += ' - Causa riscontrata: ' + closing_category
            res['name'] = line_name
        else:
            note = []
            names_list = []
            for line in analytic_lines:
                # set invoice_line_note
                details = []
                if data.get('date', False):
                    details.append(line['date'])
                if data.get('time', False):
                    if line['product_uom_id']:
                        details.append("%s %s" % (line.unit_amount, line.product_uom_id.name))
                    else:
                        details.append("%s" % (line['unit_amount'], ))
                if data.get('name', False):
                    if not data.get('date', False) and not data.get('time', False):
                        if line['name'] not in names_list:
                            names_list.append(line['name'])
                    else:
                        details.append(line['name'])
                if details:
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))
            if note:
                if names_list and not data.get('date', False) and not data.get('time', False):
                    note.append(u' - '.join(map(lambda x: unicode(x) or '', names_list)))
                res['name'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))
        return res
