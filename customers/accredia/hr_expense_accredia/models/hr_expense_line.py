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
import openerp.addons.decimal_precision as dp


class hr_expense_line(orm.Model):
    _inherit = 'hr.expense.line'

    _order = "date_value asc, sequence"

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        if context is None:
            context = {}
        warning = {}
        res = super(hr_expense_line, self).onchange_product_id(cr, uid, ids, product_id, context)

        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            t_expense_type = product.expense_type
            t_product_type = product.type
            if t_expense_type == 'car_own' and t_product_type == 'service':
                t_partner_id = context.get('partner_id', None)
                if t_partner_id:
                    partner_data = self.pool.get('res.partner').browse(cr, uid, t_partner_id)
                    if partner_data and partner_data.km_rate:
                        res['value']['unit_amount'] = partner_data.km_rate
            if not t_expense_type:
                warning = {
                    'title': _('Attenzione!'),
                    'message': _("Il prodotto selezionato ha il campo 'Tipo di Spesa' vuoto. Per favore impostare il campo 'Tipo di Spesa' oppure selezionare un altro prodotto")
                }

        if warning:
            res['warning'] = warning
        return res

    def _amount(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        cr.execute("SELECT l.id,COALESCE(SUM(l.unit_amount*l.unit_quantity),0) AS amount FROM hr_expense_line l WHERE id IN %s GROUP BY l.id ",(tuple(ids),))
        res = dict(cr.fetchall())

        for record in self.browse(cr, uid, ids, context=context):

            if record.expense_id.currency_rate and \
               record.currency_id and \
               record.currency_id != record.expense_id.currency_id and \
               record.expense_id.currency_rate != 0:
                res[record.id] *= record.expense_id.currency_rate
        return res

    _columns = {'total_amount': fields.function(_amount, string='Total',
                                                digits_compute=dp.get_precision('Account')),
                'already_paid': fields.selection([('prepaid', 'Prepagata'),
                                                  ('card', 'Carta di credito'),
                                                  ], 'Già Pagato', select=True),
                'task_id': fields.related('expense_id',
                                          'task_id',
                                          type="many2one",
                                          relation="project.task",
                                          store=False,
                                          string="Audit",
                                          required=False,
                                          readonly=True),
                'own_car_use': fields.boolean('Hidden'),
                }

    def create(self, cr, user, vals, context=None):
        if context is None:
            context = {}

        if 'expense_id' not in vals or not vals['expense_id']:
            raise orm.except_orm(_('Errore!'),
                                 _('Il campo expense_id è obbligatorio!'))

        expense_obj = self.pool.get('hr.expense.expense')
        record = expense_obj.browse(cr, user, vals['expense_id'], context=context)
        if record and record.task_id and record.task_id.project_id:
            if 'analytic_account' not in vals or not vals['analytic_account']:
                t_analytic_account_id = record.task_id.project_id.analytic_account_id
                vals.update({'analytic_account': t_analytic_account_id.id, })

        if 'currency_id' not in vals or not vals['currency_id']:
            vals.update({'currency_id': None, })
            if record and record.currency_id:
                vals.update({'currency_id': record.currency_id.id, })

        res = super(hr_expense_line, self).create(cr, user, vals, context)

        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'analytic_account' in vals and not vals['analytic_account']:
            for record in self.browse(cr, uid, ids, context=context):
                if record.expense_id and record.expense_id.task_id and record.expense_id.task_id.project_id:
                    t_analytic_account_id = record.expense_id.task_id.project_id.analytic_account_id
                    vals.update({'analytic_account': t_analytic_account_id.id,})
        return super(hr_expense_line, self).write(cr, uid, ids, vals, context=context)
