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

from openerp import fields, models, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    task_id = fields.Many2one('project.task', string='Riferimento')

    @api.multi
    def action_button_confirm(self):

        res = super(SaleOrder, self).action_button_confirm()

        for sale_data in self:

            project_data = sale_data.project_id
            if project_data and project_data.state != 'template':

                if project_data.accreditation_project_type and project_data.accreditation_project_type.is_experimental_verification:

                    # recupera dati
                    if not sale_data.task_id:
                        raise except_orm(_('Error!'),
                                         _('Nessuna attività definita per Generazione Riga da Fatturare a Cliente')
                                         )

                    t_name = sale_data.name or ''
                    t_date = sale_data.date_order
                    t_account_id = sale_data.project_id and sale_data.project_id.id or None

                    invoice_factor_obj = self.env['hr_timesheet_invoice.factor']
                    t_to_invoice_ids = invoice_factor_obj.search([('customer_name', 'like', '100%')])
                    t_to_invoice = t_to_invoice_ids and t_to_invoice_ids[0] or None

                    t_journal_id = sale_data.project_id and sale_data.project_id.department_id and sale_data.project_id.department_id.experimental_journal_id and sale_data.project_id.department_id.experimental_journal_id.id or None
                    if not t_journal_id:
                        raise except_orm(_('Error!'),
                                         _('Nessun Giornale Analitico definito per Generazione Riga da Fatturare a Cliente')
                                         )

                    t_customer_id = sale_data.partner_invoice_id and sale_data.partner_invoice_id.id or None
                    if not t_customer_id:
                        raise except_orm(_('Error!'),
                                         _('Nessun Indirizzo Fatturazione Cliente definito per Generazione Riga da Fatturare a Cliente')
                                         )

                    # TODO per ogni riga del preventivo
                    for sale_line_data in sale_data.order_line:

                        t_product_data = sale_line_data.product_id
                        t_product_id = sale_line_data.product_id and sale_line_data.product_id.id or None
                        if not t_product_id:
                            raise except_orm(_('Error!'),
                                             _('Nessun Prodotto definito per Generazione Riga da Fatturare a Cliente')
                                             )

                        t_product_uom = sale_line_data.product_uom and sale_line_data.product_uom.id or None
                        qty = sale_line_data.product_uom_qty
                        unit_price = sale_line_data.price_unit

                        t_account = None
                        t_description = sale_line_data.name
                        if t_product_data:
                            categ_data = t_product_data.categ_id or None
                            prop_data = t_product_data.property_account_income
                            t_account = prop_data and prop_data.id or None
                            if not t_account:
                                prop_data = categ_data.property_account_income_categ
                                t_account = prop_data and prop_data.id or None
                            if not t_account:
                                raise except_orm(_('Error!'),
                                                 _('There is no income account defined '
                                                   'for this product: "%s" (id:%d).') %
                                                 (sale_data.type_id.product_line_id.name, t_product_id,))

                        # crea attività da fatturare
                        vals = {'name': t_description,
                                'ref': t_name,
                                'date': t_date,
                                'account_id': t_account_id,
                                'user_id': self._uid,
                                'unit_amount': qty,
                                'amount': - unit_price * qty,
                                'general_account_id': t_account,
                                'product_uom_id': t_product_uom,
                                'journal_id': t_journal_id,
                                'product_id': t_product_id,
                                'to_invoice': t_to_invoice and t_to_invoice.id or None,
                                'customer_id': t_customer_id,
                                }
                        self.env['account.analytic.line'].create(vals)

        return res
