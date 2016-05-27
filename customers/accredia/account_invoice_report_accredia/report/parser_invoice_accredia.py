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

import time
from openerp.report import report_sxw
from openerp import pooler
import os
import urllib2
#import urlparse
try:
    import simplejson as json
except ImportError:
    import json     # noqa
from openerp.addons.account_financial_report_webkit.report.common_partner_reports import CommonPartnersReportHeaderWebkit
from openerp.addons.account_financial_report_webkit.report.webkit_parser_header_fix import HeaderFooterTextWebKitParser


class parser_invoice_report_accredia(report_sxw.rml_parse, CommonPartnersReportHeaderWebkit):
    _name = 'account.invoice.report.accredia.isa'

    def __init__(self, cr, uid, name, context=None):
        self.cr = cr
        self.uid = uid
        self.tasks_list = []
        self.lines = []
        self.lines_dict = {}
        if context is None:
            context = {}
        super(parser_invoice_report_accredia,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_move_line': self._get_move_line,
            'get_order_invoice_line': self._get_order_invoice_line,
            'get_task': self._get_task,
            'get_lines': self._get_lines,
            'get_lines_dict': self._get_lines_dict,
            'get_line_values': self._get_line_values,
            'get_grouped_taxes': self._get_grouped_taxes,
            'count_lines': self._count_lines,
            'get_uom': self._get_uom,
        })
        self.context = context

    def _get_uom(self, uom_id):
        context = {'lang': 'it_IT',}
        t_name = self.pool.get('product.uom').browse(self.cr, self.uid, uom_id, context).name
        return t_name

    def _get_move_line(self, invoice):
        move_lines = []
        if invoice and invoice.move_id:
            hrs = pooler.get_pool(self.cr.dbname).get('account.move.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('move_id', '=', invoice.move_id.id),
                                   ('date_maturity', '!=', False), ],
                                  order='date_maturity')
            move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        elif invoice:

            invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
            payments_preview = []
            t_amount_total = invoice.amount_total
            if (hasattr(invoice, 'has_wht') and invoice.has_wht):
                t_amount_total = invoice.net_pay
            obj_pt = pooler.get_pool(self.cr.dbname).get('account.payment.term')
            if invoice.payment_term:
                p_type = obj_pt.name_get(self.cr, self.uid, [invoice.payment_term.id], self.localcontext)[0][1]
                pterm_list = obj_pt.compute(self.cr, self.uid, invoice.payment_term.id,
                                            t_amount_total, date_ref=invoice.date_invoice)
                if pterm_list:
                    for line in pterm_list:
                        t_pline = invoice_obj._get_preview_line(invoice, line)
                        payments_preview.append(t_pline)

                    if (hasattr(invoice, 'has_wht') and invoice.has_wht):
                        t_new_pterm = invoice_obj._get_wht_due_line(self.cr, self.uid,
                                                          invoice, pterm_list)
                        payments_preview.append(t_new_pterm)

            move_lines = payments_preview
        return move_lines

    def _get_order_invoice_line(self, invoice_id, limit_page, offset_page):
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        invoice_lines = []
        if invoice_data and invoice_data.invoice_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('account.invoice.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('invoice_id', '=', invoice_id), ],
                                  limit=limit_page,
                                  offset=offset_page,
                                  order="project_id,task_id,product_expense_type")
            t_counter = 0

            prev_project_id = None
            prev_task_id = None
            prev_product_expense_type = ''

            prec_count                   = 0
            prec_product_id_code         = ''
            prec_product_id_type         = ''
            prec_product_id_expense_type = ''
            prec_product_id_name         = ''
            prec_product_id_uom_id       = None
            prec_task_id                 = None
            prec_task_id_description     = ''
            prec_name                    = ''
            prec_uos_id                  = None
            prec_uos_id_name             = ''
            prec_quantity                = 0
            prec_price_subtotal          = 0.0
            prec_price_unit              = 0.0
            prec_taxes                   = []

            for t_line in hrs.browse(self.cr, self.uid, hrs_list):
                t_tax_list = []

                if t_line.expense_line_id and t_line.expense_line_id.id not in self.lines:
                    self.lines.append(t_line.expense_line_id.id)
                    self.lines_dict.update({t_line.expense_line_id.id: t_line.id,})

                if t_line.task_id and t_line.task_id.id not in self.tasks_list:
                    self.tasks_list.append(t_line.task_id.id)

                for t_tax_line in t_line.invoice_line_tax_id:
                    if (not t_tax_line.tax_code_id) or (t_tax_line.tax_code_id and not t_tax_line.tax_code_id.notprintable):
                        if t_tax_line.tax_code_id and t_tax_line.tax_code_id.code:
                            t_tax_list.append(t_tax_line.tax_code_id.code)

                if t_line.project_id and t_line.task_id \
                   and prev_project_id == t_line.project_id.id \
                   and prev_task_id == t_line.task_id.id \
                   and t_line.product_id \
                   and t_line.product_id.expense_type \
                   and prev_product_expense_type:

                    prec_count                   = prec_count

                    prec_product_id_code         = t_line.product_id and t_line.product_id.code or ''
                    prec_product_id_type         = t_line.product_id and t_line.product_id.type or ''
                    prec_product_id_expense_type = t_line.product_id and t_line.product_id.expense_type or ''
                    prec_product_id_name         = 'Rimborso Spese ispettori (vedi allegato)'
                    prec_product_id_uom_id       = t_line.product_id and t_line.product_id.uom_id and t_line.product_id.uom_id.id or None
                    prec_task_id                 = t_line.task_id or None
                    prec_task_id_description     = t_line.task_id and t_line.task_id.description or ''
                    prec_name                    = t_line.name or ''
                    prec_uos_id                  = t_line.uos_id and t_line.uos_id.id or None
                    prec_uos_id_name             = t_line.uos_id and t_line.uos_id.name or ''
                    prec_quantity                = prec_quantity + t_line.quantity or 0
                    prec_price_subtotal          = prec_price_subtotal + t_line.price_subtotal or 0.0
                    prec_price_unit              = prec_price_unit + t_line.price_unit or 0.0
                    for e in t_tax_list:
                        if e not in prec_taxes:
                            prec_taxes                   = prec_taxes + e
                elif t_line.project_id \
                    and t_line.task_id \
                    and prev_project_id == t_line.project_id.id \
                    and prev_task_id == t_line.task_id.id \
                    and t_line.product_id \
                    and not t_line.product_id.expense_type \
                    and not prev_product_expense_type:

                    prec_count                   = prec_count

                    prec_product_id_code         = t_line.product_id and t_line.product_id.code or ''
                    prec_product_id_type         = t_line.product_id and t_line.product_id.type or ''
                    prec_product_id_expense_type = t_line.product_id and t_line.product_id.expense_type or ''
                    prec_product_id_name         = t_line.task_id and t_line.task_id.description or (t_line.product_id and t_line.product_id.name) or ''
                    prec_product_id_uom_id       = t_line.product_id and t_line.product_id.uom_id and t_line.product_id.uom_id.id or None
                    prec_task_id                 = t_line.task_id or None
                    prec_task_id_description     = t_line.task_id and t_line.task_id.description or ''
                    prec_name                    = t_line.name or ''
                    prec_uos_id                  = t_line.uos_id and t_line.uos_id.id or None
                    prec_uos_id_name             = t_line.uos_id and t_line.uos_id.name or ''
                    prec_quantity                = prec_quantity + t_line.quantity or 0
                    prec_price_subtotal          = prec_price_subtotal + t_line.price_subtotal or 0.0
                    prec_price_unit              = prec_price_unit + t_line.price_unit or 0.0
                    for e in t_tax_list:
                        if e not in prec_taxes:
                            prec_taxes                   = prec_taxes + e

                else:
                    if prec_count:
                        t_dict = {'count': prec_count,
                                  'product_id_code': prec_product_id_code,
                                  'product_id_type': prec_product_id_type,
                                  'product_id_expense_type': prec_product_id_expense_type,
                                  'product_id_name': prec_product_id_name,
                                  'product_id_uom_id': prec_product_id_uom_id,
                                  'task_id': prec_task_id,
                                  'task_id_description': prec_task_id_description,
                                  'name': prec_name,
                                  'uos_id': prec_uos_id,
                                  'uos_id_name': prec_uos_id_name,
                                  'quantity': prec_quantity,
                                  'price_subtotal': prec_price_subtotal,
                                  'price_unit': prec_price_unit,
                                  'taxes': prec_taxes,
                                  }

                        invoice_lines.append(t_dict)


                    t_counter = t_counter + 1

                    prec_count                   = t_counter
                    prec_product_id_code         = t_line.product_id and t_line.product_id.code or ''
                    prec_product_id_type         = t_line.product_id and t_line.product_id.type or ''
                    prec_product_id_expense_type = t_line.product_id and t_line.product_id.expense_type or ''
                    prec_product_id_name         = t_line.product_id and t_line.product_id.expense_type and 'Rimborso Spese ispettori (vedi allegato)' or (t_line.task_id and t_line.task_id.description) or (t_line.product_id and t_line.product_id.name) or ''
                    prec_product_id_uom_id       = t_line.product_id and t_line.product_id.uom_id and t_line.product_id.uom_id.id or None
                    prec_task_id                 = t_line.task_id or None
                    prec_task_id_description     = t_line.task_id and t_line.task_id.description or ''
                    prec_name                    = t_line.name or ''
                    prec_uos_id                  = t_line.uos_id and t_line.uos_id.id or None
                    prec_uos_id_name             = t_line.uos_id and t_line.uos_id.name or ''
                    prec_quantity                = t_line.quantity or 0
                    prec_price_subtotal          = t_line.price_subtotal or 0.0
                    prec_price_unit              = t_line.price_unit or 0.0
                    if t_tax_list:
                        prec_taxes                   = t_tax_list and ','.join(e for e in t_tax_list) or ''

                prev_project_id = t_line.project_id and t_line.project_id.id
                prev_task_id = t_line.task_id and t_line.task_id.id
                prev_product_expense_type = t_line.product_id and t_line.product_id.expense_type or ''

            if prec_count:
                t_dict = {'count': prec_count,
                          'product_id_code': prec_product_id_code,
                          'product_id_type': prec_product_id_type,
                          'product_id_expense_type': prec_product_id_expense_type,
                          'product_id_name': prec_product_id_name,
                          'product_id_uom_id': prec_product_id_uom_id,
                          'task_id': prec_task_id,
                          'task_id_description': prec_task_id_description,
                          'name': prec_name,
                          'uos_id': prec_uos_id,
                          'uos_id_name': prec_uos_id_name,
                          'quantity': prec_quantity,
                          'price_subtotal': prec_price_subtotal,
                          'price_unit': prec_price_unit,
                          'taxes': prec_taxes,
                          }

                invoice_lines.append(t_dict)

            if invoice_lines:
                return sorted(invoice_lines, key=lambda k: k['count'])
        return []

    def _count_lines(self, invoice_id):
        t_counter = 0

        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)

        if invoice_data and invoice_data.invoice_line:
            hrs_list = []
            hrs = pooler.get_pool(self.cr.dbname).get('account.invoice.line')
            hrs_list = hrs.search(self.cr, self.uid,
                                  [('invoice_id', '=', invoice_id), ],
                                  order="project_id,task_id,product_expense_type")
            t_counter = 0

            prev_project_id = None
            prev_task_id = None
            prev_product_expense_type = ''

            prec_count = 0
            num_lines = 0

            for t_line in hrs.browse(self.cr, self.uid, hrs_list):

                if t_line.project_id and t_line.task_id \
                   and prev_project_id == t_line.project_id.id \
                   and prev_task_id == t_line.task_id.id \
                   and t_line.product_id \
                   and t_line.product_id.expense_type \
                   and prev_product_expense_type:

                    prec_count = prec_count

                elif t_line.project_id \
                    and t_line.task_id \
                    and prev_project_id == t_line.project_id.id \
                    and prev_task_id == t_line.task_id.id \
                    and t_line.product_id \
                    and not t_line.product_id.expense_type \
                    and not prev_product_expense_type:

                    prec_count = prec_count

                else:

                    t_counter = t_counter + 1

                prev_project_id = t_line.project_id and t_line.project_id.id
                prev_task_id = t_line.task_id and t_line.task_id.id
                prev_product_expense_type = t_line.product_id and t_line.product_id.expense_type or ''

            if prec_count:
                # TODO ???
                num_lines = num_lines +1

        return t_counter

    def _get_task(self):
        hrs = pooler.get_pool(self.cr.dbname).get('project.task')
        tasks_data = hrs.browse(self.cr, self.uid, self.tasks_list)
        return tasks_data

    def _get_lines(self):
        return self.lines

    def _get_lines_dict(self):
        return self.lines_dict

    def _get_line_values(self, line_id):
        hrs = pooler.get_pool(self.cr.dbname).get('account.invoice.line')
        line_data = hrs.browse(self.cr, self.uid, line_id)
        return line_data

    def _get_grouped_taxes(self, invoice_id):
        t_count = 0
        t_list = []
        invoice_lines = {}
        invoice_obj = pooler.get_pool(self.cr.dbname).get('account.invoice')
        invoice_data = invoice_obj.browse(self.cr, self.uid, invoice_id)
        for t_line in invoice_data.tax_line:
            if (not t_line.tax_code_id) or (t_line.tax_code_id and not t_line.tax_code_id.notprintable):

                t_code = t_line.tax_code_id and t_line.tax_code_id.code or '-'
                if t_code not in t_list:
                    t_list.append(t_code)
                    invoice_lines[t_count] = {'code': t_code,
                                              'name': t_line.name or '',
                                              'base': t_line.base or 0.0,
                                              'amount': t_line.amount or 0.0,
                                              }
                    t_count = t_count + 1
                else:
                    for t_dict in invoice_lines:
                        if invoice_lines[t_dict]['code'] == t_code:
                            invoice_lines[t_dict]['base'] += t_line.base or 0.0
                            invoice_lines[t_dict]['amount'] += t_line.amount or 0.0
                            break

        return invoice_lines

HeaderFooterTextWebKitParser('report.fattura_accredia_report2',
                             'account.invoice',
                             os.path.dirname(os.path.realpath(__file__)) + '/invoice_accredia.mako',
                             parser=parser_invoice_report_accredia)
