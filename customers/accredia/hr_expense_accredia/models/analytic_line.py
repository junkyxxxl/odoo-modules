# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from openerp.osv import fields, orm
from openerp.tools.translate import _


class account_analytic_line(orm.Model):
    _inherit = 'account.analytic.line'

    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        res = {'value': {'task_id': None,
                         'partner_id': None,
                         }
               }

        if user_id:
            user_obj = self.pool.get('res.users')
            user_data = user_obj.browse(cr, uid, user_id)
            if user_data.partner_id:
                t_partner_id = user_data.partner_id.id

                res['value']['task_id'] = None
                res['value']['partner_id'] = t_partner_id

        return res

    _columns = {
        'project_id': fields.related('task_id',
                                     'project_id',
                                     type="many2one",
                                     relation="project.project",
                                     store=True,  # necessario per il groupby nel filtro
                                     string="Pratica",
                                     required=False,
                                     readonly=True),
        'customer_id': fields.related('account_id',
                                      'partner_id',
                                      type="many2one",
                                      relation="res.partner",
                                      store=True,  # necessario per il groupby nel filtro
                                      string="Cliente",
                                      required=False,
                                      readonly=True),
        'partner_id': fields.related('user_id',
                                     'partner_id',
                                     type='many2one',
                                     store=False,
                                     readonly=True,
                                     relation='res.partner',
                                     string='Persona Fisica'),
        'product_category_id': fields.related('product_id',
                                              'categ_id',
                                              type="many2one",
                                              relation="product.category",
                                              store=True,
                                              string="Categoria Prodotto",
                                              required=False,
                                              readonly=True),
        }

    def invoice_cost_create(self, cr, uid, ids, data=None, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        account_payment_term_obj = self.pool.get('account.payment.term')
        invoice_obj = self.pool.get('account.invoice')
        product_obj = self.pool.get('product.product')
        invoice_factor_obj = self.pool.get('hr_timesheet_invoice.factor')
        fiscal_pos_obj = self.pool.get('account.fiscal.position')
        product_uom_obj = self.pool.get('product.uom')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        invoices = []
        if context is None:
            context = {}
        if data is None:
            data = {}

        partner_dict = {}

        # prepare for iteration on cig and partner
        for line in self.pool.get('account.analytic.line').browse(cr, uid, ids, context=context):
            if line.account_id and line.account_id.partner_id and line.account_id.partner_id.id:
                t_partner_id = line.account_id.partner_id.id
                t_account_id = line.account_id.id
                t_codice_cig = line.task_id and line.task_id.codice_cig or line.task_id.project_id and line.task_id.project_id.codice_cig or None

                if t_codice_cig not in partner_dict:
                    partner_dict[t_codice_cig] = {}

                if t_partner_id not in partner_dict[t_codice_cig]:
                    partner_dict[t_codice_cig][t_partner_id] = {}

                if t_account_id not in partner_dict[t_codice_cig][t_partner_id]:
                    partner_dict[t_codice_cig][t_partner_id][t_account_id] = []

                partner_dict[t_codice_cig][t_partner_id][t_account_id].append(line.id)

        for t_cig in partner_dict:
            for temp_partner_id in partner_dict[t_cig]:
                partner = partner_obj.browse(cr, uid, temp_partner_id, context=context)
                temp_account_id = None
                for t_acc in partner_dict[t_cig][temp_partner_id]:
                    temp_account_id = t_acc
                account = analytic_account_obj.browse(cr, uid, temp_account_id, context=context)
                date_due = False
                if partner.property_payment_term:
                    pterm_list = account_payment_term_obj.compute(cr, uid,
                                                                  partner.property_payment_term.id, value=1,
                                                                  date_ref=time.strftime('%Y-%m-%d'))
                    if pterm_list:
                        pterm_list = [line[0] for line in pterm_list]
                        pterm_list.sort()
                        date_due = pterm_list[-1]

                partner_invoice_id = partner.id
                for child_data in partner.child_ids:
                    if child_data.type == 'invoice':
                        partner_invoice_id = child_data.id
                        break

                curr_invoice = {
                    'name': time.strftime('%d/%m/%Y') + ' - '+partner.name,
                    'partner_id': partner_invoice_id,
                    'company_id': account.company_id.id,
                    'payment_term': partner.property_payment_term.id or False,
                    'account_id': partner.property_account_receivable.id,
                    'currency_id': account.currency_id.id,
                    'date_due': date_due,
                    'fiscal_position': partner.property_account_position.id,
                    'codice_cig': t_cig,
                }
                context2 = context.copy()
                context2['lang'] = partner.lang
                # set company_id in context, so the correct default journal will be selected
                context2['force_company'] = curr_invoice['company_id']
                # set force_company in context so the correct product properties are selected (eg. income account)
                context2['company_id'] = curr_invoice['company_id']

                last_invoice = invoice_obj.create(cr, uid, curr_invoice, context=context2)
                invoices.append(last_invoice)

                t_line_id = "IN " + str(tuple(partner_dict[t_cig][partner.id][account.id]))
                if len(partner_dict[t_cig][partner.id][account.id]) == 1:
                    t_line_id = "= " + str(partner_dict[t_cig][partner.id][account.id][0])
                cr.execute("""SELECT line.id, product_id, user_id, to_invoice, amount, unit_amount, product_uom_id, task_id, account_id
                        FROM account_analytic_line as line
                        WHERE line.id """ + t_line_id + """ AND to_invoice IS NOT NULL""")

                for line_id, product_id, _, factor_id, total_price, qty, uom, task_id, account_id in cr.fetchall():
                    context2.update({'uom': uom})

                    product = product_obj.browse(cr, uid, product_id, context=context2)

                    if product and not qty:
                        raise orm.except_orm(_("Errore!"),
                                             _("la quantità non può essere nulla per il prodotto '%s'.") % product.name)

                    unit_price = total_price*-1.0 / qty

                    factor = invoice_factor_obj.browse(cr, uid, factor_id, context=context2)
                    # factor_name = factor.customer_name and line_name + ' - ' + factor.customer_name or line_name
                    factor_name = factor.customer_name
                    curr_line = {
                        'price_unit': unit_price,
                        'quantity': qty,
                        'product_id': product_id or False,
                        'discount': factor.factor,
                        'invoice_id': last_invoice,
                        'name': factor_name,
                        'uos_id': uom,
                        'account_analytic_id': account_id,
                        'task_id': task_id,
                    }

                    if product:
                        factor_name = product_obj.name_get(cr, uid, [product_id], context=context2)[0][1]
                        if factor.customer_name:
                            factor_name += ' - ' + factor.customer_name

                        general_account = product.property_account_income or product.categ_id.property_account_income_categ
                        if not general_account:
                            raise orm.except_orm(_("Configuration Error!"), _("Please define income account for product '%s'.") % product.name)
                        taxes = product.taxes_id or general_account.tax_ids
                        tax = fiscal_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes)
                        curr_line.update({'invoice_line_tax_id': [(6,0,tax )],
                                          'name': factor_name,
                                          'invoice_line_tax_id': [(6,0,tax)],
                                          'account_id': general_account.id,
                                          })
                    #
                    # Compute for lines
                    #
                    cr.execute("SELECT * FROM account_analytic_line WHERE account_id = %s and id = " + str(line_id) + " AND product_id=%s and to_invoice=%s ORDER BY account_analytic_line.date", (account.id, product_id, factor_id))

                    line_ids = cr.dictfetchall()
                    note = []
                    for line in line_ids:
                        # set invoice_line_note
                        details = []
                        if data.get('date', False):
                            details.append(line['date'])
                        if data.get('time', False):
                            if line['product_uom_id']:
                                details.append("%s %s" % (line['unit_amount'], product_uom_obj.browse(cr, uid, [line['product_uom_id']], context2)[0].name))
                            else:
                                details.append("%s" % (line['unit_amount'], ))
                        if data.get('name', False):
                            details.append(line['name'])
                        note.append(u' - '.join(map(lambda x: unicode(x) or '', details)))
                    if note:
                        curr_line['name'] += "\n" + ("\n".join(map(lambda x: unicode(x) or '', note)))
                    invoice_line_obj.create(cr, uid, curr_line, context=context)
                    cr.execute("update account_analytic_line set invoice_id=%s WHERE account_id = %s and id IN %s", (last_invoice, account.id, tuple(ids)))

                invoice_obj.button_reset_taxes(cr, uid, [last_invoice], context)
        return invoices
