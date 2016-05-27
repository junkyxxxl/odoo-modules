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
from openerp import fields, models, api
from openerp.tools.translate import _
from datetime import datetime, timedelta
from openerp.exceptions import except_orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ProjectTaskWork(models.Model):

    _inherit = "project.task.work"

    @api.one
    def do_create_audit(self):

        # recupera dati
        t_project_id = self.project_id and self.project_id.id or None
        product_uom = None
        try:
            product_uom = self.env['ir.model.data'].get_object_reference('product', 'product_uom_day')
        except ValueError:
            pass

        if product_uom:
            product_uom = product_uom[1]

        t_date_start = self.date and self.date[:10] or None
        t_date_end = self.date_end and self.date_end[:10] or None

        start_date = None
        end_date = None
        t_duration = None
        if t_date_start:
            start_date = datetime.strptime(t_date_start, "%Y-%m-%d")
        if t_date_end:
            end_date = datetime.strptime(t_date_end, "%Y-%m-%d") + timedelta(days=1)
        if start_date and end_date:
            t_int_diff = end_date-start_date
            t_int_days = t_int_diff.days
            t_duration = abs(t_int_days)

        t_type_audit_visit = self.type_id.type_audit_visit and self.type_id.type_audit_visit.id or None
        t_type_audit_doc_review = self.type_id.type_audit_doc_review and self.type_id.type_audit_doc_review.id or None
        t_audit_type_id = self.task_id.stage_id and self.task_id.stage_id.id or None
        t_audit_category_id = self.task_id.category_id and self.task_id.category_id.id or None
        t_action_type_id = self.type_id and self.type_id.id or None
        t_audit_task_type = self.type_id and self.type_id.audit_task_type or ''

        if t_audit_task_type != 'to_plan':
            # crea audit
            vals = {'name': 'Visita Ispettiva',  # TODO
                    'project_id': t_project_id,
                    'date_start': t_date_start,
                    'date_end': t_date_end,
                    'product_uom': product_uom,
                    'duration': t_duration,  # TODO
                    'state': 'draft',
                    'type_audit_visit': t_type_audit_visit,
                    'type_audit_doc_review': t_type_audit_doc_review,
                    'type_audit_type_id': t_audit_type_id,
                    'type_audit_category_id': t_audit_category_id,
                    'action_type_id': t_action_type_id,
                    'audit_task_type': t_audit_task_type,
                    }
            res = self.env['project.phase'].create(vals)

            # log
            datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
            vals = {'work_id': self.id,
                    'doclite_action_type': 'create_audit',
                    'phase_id': res.id,
                    'exec_date': datetime_today,
                    'user_id': self._uid,
                    }
            self.env['accreditation.task.work.log'].create(vals)
        else:
            # log
            datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
            vals = {'work_id': self.id,
                    'doclite_action_type': 'display_to_plan_audit',
                    'to_plan_project_id': t_project_id,
                    'exec_date': datetime_today,
                    'user_id': self._uid,
                    }
            self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_line_to_invoice(self):

        # recupera dati
        t_project_id = self.project_id and self.project_id.id or None
        t_task_id = self.task_id and self.task_id.id or None
        t_task_name = self.task_id and self.task_id.name or ''
        t_journal_id = self.type_id.journal_id and self.type_id.journal_id.id or None
        t_product_id = self.type_id.product_line_id and self.type_id.product_line_id.id or None
        t_to_invoice = self.type_id.to_invoice and self.type_id.to_invoice.id or None
        t_account_id = self.project_id and self.project_id.analytic_account_id.id or None
        t_entity_id = self.project_id.partner_id and self.project_id.partner_id.id or None
        #t_date = fields.Date.context_today(self)
        t_date = self.task_id.date_start
        t_user_id = self.user_id.id or None
        t_phase_id = self.task_id.phase_id

        if t_phase_id:
            allocation_obj = self.env['project.user.allocation'].search([('project_id', '=', self.project_id.id),
                                                                         ('user_id', '=',self.user_id.id),
                                                                         ('phase_id', '=', t_phase_id.id),
                                                                         ('task_audit_type_id', '=', self.type_id.id),
                                                                         ('date_start', '=', t_date[0:10]),
                                                                         ('date_end','=', self.task_id.date_end[0:10])])

            qty = allocation_obj.num_days
        else:
            qty = 1.0

        if not t_project_id:
            raise except_orm(_('Error!'),
                             _('Nessuna Pratica definita per Generazione Riga da Fatturare a Cliente'))
        if not t_product_id:
            raise except_orm(_('Error!'),
                             _('Nessun Prodotto definito per Generazione Riga da Fatturare a Cliente'))
        if not t_account_id:
            raise except_orm(_('Error!'),
                             _('Nessun Conto Analitico definito per Generazione Riga da Fatturare a Cliente'))
        if not t_journal_id:
            raise except_orm(_('Error!'),
                             _('Nessun Giornale Analitico definito per Generazione Riga da Fatturare a Cliente'))
        if not t_task_id:
            raise except_orm(_('Error!'),
                             _('Nessuna attività definita per Generazione Riga da Fatturare a Cliente'))
        if not t_entity_id:
            raise except_orm(_('Error!'),
                             _('Nessun Cliente definito per Generazione Riga da Fatturare a Cliente'))

        t_account = None
        categ_data = self.type_id.product_line_id.categ_id or None
        if self.type_id.journal_id.type != 'sale':
            prop_data = self.type_id.product_line_id.property_account_expense
            t_account = prop_data and prop_data.id or None
            if not t_account:
                prop_data = categ_data.property_account_expense_categ
                t_account = prop_data and prop_data.id or None
            if not t_account:
                raise except_orm(_('Error!'),
                                 _('There is no expense account defined '
                                   'for this product: "%s" (id:%d).') %
                                 (self.type_id.product_line_id.name, t_product_id,))
        else:
            prop_data = self.type_id.product_line_id.property_account_income
            t_account = prop_data and prop_data.id or None
            if not t_account:
                prop_data = categ_data.property_account_income_categ
                t_account = prop_data and prop_data.id or None
            if not t_account:
                raise except_orm(_('Error!'),
                                 _('There is no income account defined '
                                   'for this product: "%s" (id:%d).') %
                                 (self.type_id.product_line_id.name, t_product_id,))

        product_uom = None
        try:
            product_uom = self.env['ir.model.data'].get_object_reference('product', 'product_uom_day')
        except ValueError:
            pass

        if product_uom:
            product_uom = product_uom[1]

        # TODO è il listino corretto?
        t_pricelist = self.project_id.partner_id and self.project_id.partner_id.property_product_pricelist or None
        if not t_pricelist:
            raise except_orm(_('Error!'),
                             _('Nessun listino di vendita definito per Generazione Riga da Fatturare a Cliente'))

        pricelist_pool = self.pool.get('product.pricelist')
        unit_price = pricelist_pool.price_get(self._cr, self._uid,
                                              [t_pricelist.id],
                                              t_product_id,
                                              1.0,
                                              self.project_id.partner_id.id)[t_pricelist.id]


        # crea attività da fatturare
        vals = {'name': t_task_name,
                'unit_amount': qty,
                'amount': - unit_price * qty,
                'general_account_id': t_account,
                'date': t_date,  # TODO
                'product_uom_id': product_uom,
                'journal_id': t_journal_id,
                'product_id': t_product_id,
                'to_invoice': t_to_invoice,
                'account_id': t_account_id,
                'task_id' : t_task_id,
                'user_id' : t_user_id,
                }
        res = self.env['account.analytic.line'].create(vals)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'create_line_to_invoice',
                'analytic_line_id': res.id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_quotation(self):

        # recupera dati
        t_account_analytic_id = self.project_id.analytic_account_id and self.project_id.analytic_account_id.id or None
        t_task_id = self.task_id and self.task_id.id or None
        t_task_obj = self.env['project.task'].browse(t_task_id)
        t_product_quotation_id = self.type_id.product_quotation_id and self.type_id.product_quotation_id.id or None
        t_product_quotation_name = self.type_id.product_quotation_id and self.type_id.product_quotation_id.name or None
        t_date = fields.Date.context_today(self)

        if not t_product_quotation_id:
            raise except_orm(_('Error!'),
                             _('Nessun Prodotto definito per Generazione Preventivo per Fornitore'))

        t_department_id = self.task_id and self.task_id.project_id and self.task_id.project_id.department_id and self.task_id.project_id.department_id.id or None

        team_list = []
        if self.task_id:
            for team_mate in self.task_id.task_team_ids:
                if team_mate.user_id.id not in team_list:
                    team_list.append(team_mate.user_id.id)

        t_date_start = self.task_id.date_start
        t_date_end = self.task_id.date_end
        t_duration = 0.0
        if t_date_end and t_date_start:
            start_date = datetime.strptime(t_date_start, "%Y-%m-%d %H:%M:%S").date()
            end_date = datetime.strptime(t_date_end, "%Y-%m-%d %H:%M:%S").date()
            t_duration = (end_date-start_date).days

        team_list_data = self.env['res.users'].browse(team_list)
        for team_user_data in team_list_data:
            partner_data = team_user_data.partner_id or None

            if partner_data.supplier:

                t_fiscal_position = None
                t_payment_term_id = None
                t_pricelist = None
                t_location_id = None
                price = 0.0
                if partner_data:
                    t_pricelist = partner_data.property_product_pricelist_purchase
                    t_fiscal_position = partner_data.property_account_position and partner_data.property_account_position.id or False
                    t_payment_term_id = partner_data.property_supplier_payment_term.id or False
                    t_location_id = partner_data.property_stock_customer.id
                    currency_id = team_user_data.company_id.currency_id
                    price = t_pricelist.price_get(t_product_quotation_id, 1.0).setdefault(t_pricelist.id, 0)
                    pricelist_currency = t_pricelist.currency_id
                    price = pricelist_currency.compute(price, currency_id)

                product_uom = None
                try:
                    product_uom = self.env['ir.model.data'].get_object_reference('product', 'product_uom_day')
                except ValueError:
                    pass

                if product_uom:
                    product_uom = product_uom[1]

                # crea preventivo fornitore
                vals = {'name': '/',
                        # TODO IntegrityError: ERRORE:  un valore chiave duplicato viola il vincolo univoco "purchase_order_name_uniq"
                        # DETTAGLI: La chiave (name, company_id)=(Visita ispettiva del 06/11/2014, 1) esiste già.
                        'task_id': t_task_id,
                        'date_order': t_date,
                        'invoice_method': 'order',
                        'partner_id': partner_data and partner_data.id or None,
                        'pricelist_id': t_pricelist and t_pricelist.id or None,
                        'payment_term_id': t_payment_term_id,
                        'fiscal_position': t_fiscal_position,
                        'department_id': t_department_id,
                        'location_id': t_location_id,
                        'origin': '',  # TODO
                        'order_line': [(0, 0, {'name': t_product_quotation_name,
                                               'product_id': t_product_quotation_id,
                                               'date_planned': t_date,  # TODO
                                               'product_qty': t_task_obj.analytic_line_ids.unit_amount or t_duration,
                                               'price_unit': price,
                                               'account_analytic_id': t_account_analytic_id,
                                               'product_uom': product_uom,
                                               })],
                        }

                res = self.env['purchase.order'].create(vals)

                #Se è settato il campo "Prodotto Nota Spese Per Preventivo Fornitore", allora viene creata
                #una nuova riga con con quantità e valore a zero per la registrazione del rimborso spese dell'ispettore esterno
                t_expense_report_supplier = self.type_id.expense_report_supplier or None
                if t_expense_report_supplier:
                    row = {'product_id': t_expense_report_supplier.id,
                           'name': t_expense_report_supplier.name,
                           'order_id': res.id,
                           'date_planned': t_date,
                           'product_qty': 0,
                           'price_unit': 0,
                           'account_analytic_id': t_account_analytic_id,
                           'product_uom': product_uom,
                           'invoiced': False,
                           'partner_id': partner_data and partner_data.id or None,
                           'state': 'draft'
                          }

                    purchase_order_line = self.env['purchase.order.line'].create(row)

                # log
                datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
                vals = {'work_id': self.id,
                        'doclite_action_type': 'create_quotation',
                        'purchase_order_id': res.id,
                        'exec_date': datetime_today,
                        'user_id': self._uid,
                        }
                self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_purchase_requisition(self):

        # recupera dati
        t_project_id = self.project_id and self.project_id.id or None
        t_task_id = self.task_id and self.task_id.id or None

        # TODO è corretto?
        t_user_id = self.user_id and self.user_id.id or None
        t_department_id = None
        t_user_data = self.env['res.users'].browse(self._uid)
        if t_user_data.department_id:
            t_department_id = t_user_data.department_id.id
        else:
            for dep in t_user_data.department_ids:
                t_department_id = dep.id
                break
        t_doclite_office_id = t_user_data.doclite_office_id and t_user_data.doclite_office_id.id or None

        t_date_start = self.task_id.date_start
        t_date_end = self.task_id.date_end

        # TODO aggiungere controllo che partner sia un fornitore?
        t_partner_id = t_user_data.partner_id and t_user_data.partner_id.id or None

        # crea richiesta di acquisto
        vals = {'task_id': t_task_id,
                'date_start': t_date_start,
                'date_end': t_date_end,
                'user_id': t_user_id,
                'exclusive': 'exclusive',
                'department_id': t_department_id,
                'requester_office_id': t_doclite_office_id,
                'project_id': t_project_id,
                }
        res = self.env['purchase.requisition'].create(vals)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'create_purchase_requisition',
                'purchase_requisition_id': res.id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_sale_quotation(self):

        # recupera dati
        t_account_analytic_id = self.project_id.analytic_account_id and self.project_id.analytic_account_id.id or None
        t_task_id = self.task_id and self.task_id.id or None
        t_date = fields.Date.context_today(self)
        t_partner_id = self.project_id.partner_id and self.project_id.partner_id.id or None

        # TODO aggiungere controllo che partner sia un cliente?
        t_fiscal_position = None
        t_payment_term_id = None
        t_pricelist_id = None
        if t_partner_id:
            customer_address = self.project_id.partner_id.address_get(['default'])
            customer = self.env['res.partner'].browse(t_partner_id)

            t_pricelist_id = customer.property_product_pricelist.id
            t_fiscal_position = customer.property_account_position and customer.property_account_position.id or False
            t_payment_term_id = customer.property_payment_term.id or False

        # crea preventivo cliente
        vals = {'name': '/',
                'task_id': t_task_id,
                'project_id': t_account_analytic_id,
                'date_order': t_date,
                'partner_id': t_partner_id,
                'partner_invoice_id': customer_address and customer_address['default'] or None,
                'partner_shipping_id': customer_address and customer_address['default'] or None,
                'pricelist_id': t_pricelist_id,
                'payment_term_id': t_payment_term_id,
                'fiscal_position': t_fiscal_position,
                'origin': '',  # TODO
                'picking_policy': 'direct',  # TODO
                'order_policy': 'manual',  # TODO
                }
        res = self.env['sale.order'].create(vals)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'create_sale_quotation',
                'sale_order_id': res.id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_update_agenda(self):

        # recupera dati
        t_name = self.task_id and self.task_id.name or None

        # TODO è corretto?
        t_user_id = self.user_id and self.user_id.id or None
        #Aggiungo il partner dell'utente
        t_partner_obj = self.env['res.users'].browse(t_user_id).partner_id

        t_date_start = self.task_id.date_start
        t_date_end = self.task_id.date_end

        if not t_date_end or not t_date_start:
            raise except_orm(_('Error!'),
                             _("Data Iniziale o Data Finale nell'attività non definite"))

        t_duration = 0.0
        if t_date_end and t_date_start:
            start_date = datetime.strptime(t_date_start, "%Y-%m-%d %H:%M:%S").date()
            end_date = datetime.strptime(t_date_end, "%Y-%m-%d %H:%M:%S").date()
            t_duration = (end_date-start_date).days

        # crea meeting
        vals = {
            'name': t_name,
            'duration': t_duration * 8,
            'description': t_name,
            'user_id': t_user_id,
            'start': t_date_start,
            'stop': t_date_end,
            'start_date': t_date_start,
            'stop_date': t_date_end,
            'state': 'open',# to block that meeting date in the calendar
        }
        res = self.env['calendar.event'].create(vals)
        res.partner_ids = t_partner_obj

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'update_agenda',
                'meeting_id': res.id,
                'exec_date': datetime_today,
                'user_id': self.user_id.id,
                #user_id': self._uid,
               }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_accreditation_request_generation(self):

        # recupera dati
        t_entity_id = self.project_id and self.project_id.partner_id and self.project_id.partner_id.id or None

        t_type = self.type_id.accreditation_request_type and self.type_id.accreditation_request_type.id or None
        t_state = self.type_id.accreditation_request_state or None
        t_user_id = self.user_id and self.user_id.is_technical_officer and self.user_id.id or None

        # crea domanda
        vals = {
            'user_id': t_user_id,
            'partner_id': t_entity_id,
            'state': t_state,
            'request_type': t_type,
        }
        res = self.env['accreditation.request'].with_context({'skip_check': True, }).create(vals)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'accreditation_request_generation',
                'request_id': res.id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.multi
    def do_doclite_action(self):

        t_doclite_action = self.type_id.doclite_action or None
        t_doclite_action_type = self.type_id.doclite_action_type or ''
        t_doclite_model = self.type_id.doclite_action_model and self.type_id.doclite_action_model.code or ''
        t_doclite_category = self.type_id.doclite_action_category and self.type_id.doclite_action_category.code or ''
        t_resource = ''
        if t_doclite_action:
            if not t_doclite_action_type:
                raise except_orm(_('Error!'),
                                 _('Nessun Tipo Azione DocLite definito'))
            if not t_doclite_model and (t_doclite_action_type in ('mail', 'document', 'folder')):
                raise except_orm(_('Error!'),
                                 _('Nessun Modello Documento DocLite definito'))
            if not t_doclite_category and t_doclite_action_type == 'archive':
                raise except_orm(_('Error!'),
                                 _('Nessuna Categoria Documento DocLite definita'))

            if t_doclite_action_type in ('mail', 'document', 'folder'):
                t_resource = '/' + t_doclite_model
            if t_doclite_action_type == 'archive':
                t_resource = '/' + t_doclite_category

        t_ids = self.env['doclite.server'].search([], limit=1)
        t_data = t_ids[0]
        t_ip = t_data.get_ip_address()
        t_port = t_data.get_port()
        t_base_path = t_data.get_base_path()

        t_script = 'doclite/OE/' + t_doclite_action_type + '/' + str(self._uid) + '/project.task.work/' + str(self.id) + t_resource

        final_url = ('http://' + str(t_ip) + ':' + str(t_port) + str(t_base_path) + str(t_script))

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'doclite_action',
                'doclite_action_name': t_doclite_action_type + ' ' + t_doclite_model,
                'action_url': 'DocLite,' + final_url,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_set_obtained_accreditation(self):

        # imposta campo obtained nell'ente
        self.project_id.partner_id.obtained = True

        if not self.date_obtained_accreditation:
            raise except_orm(_('Errore!'),
                             _('Il campo Data di Accreditamento è obbligatorio!'))

        # imposta campi Data accreditamento della pratica
        self.project_id.accreditation_date = self.date_obtained_accreditation
        if self.project_id.accreditation_date:
            date_format = datetime.strptime(self.project_id.accreditation_date, DF)
            new_date = date_format + timedelta(days=(365*4)-1)
            self.project_id.accreditation_due_date = new_date

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'set_obtained_accreditation',
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_maintenance_fee_tasks(self):

        # recupera dati
        t_project_id = self.project_id and self.project_id.id or None
        t_unit_id = self.task_id and self.task_id.unit_id and self.task_id.unit_id.id or None
        t_company_id = self.task_id and self.task_id.company_id and self.task_id.company_id.id or None
        t_stage_id = self.task_id and self.task_id.stage_id and self.task_id.stage_id.id or None
        t_name = self.task_id and self.task_id.name or ''
        t_entity_id = self.project_id.partner_id and self.project_id.partner_id.id or None
        t_partner_name = self.project_id.partner_id and self.project_id.partner_id.name or ''
        t_date = fields.Date.context_today(self)
        t_type = self.type_id.work_type_maintenance_fee_id or None

        # check tipo attività per i Diritti di Mantenimento
        if not t_type:
            raise except_orm(_('Errore!'),
                             _("Tipo di attività per Diritti di Mantenimento non specificata!"))

        # recupera gli schemi
        datetime_today = datetime.strptime(t_date, DF)
        t_year = int(datetime_today.strftime("%Y")) - 1
        domain = [
            ('customer_id', '=', t_entity_id),
            ('year', '=', str(t_year)),
        ]
        invoiced_schemas = self.env['accreditation.invoiced.schema'].search(domain)
        if not invoiced_schemas:
            raise except_orm(_('Errore!'),
                             _("Impossibile recuperare gli schemi per il Cliente %s!") % t_partner_name)

        # per ogni schema trovato crea l'attività
        for schema in invoiced_schemas:
            t_schema_name = schema.schema or ''
            # crea task
            vals = {
                'name': t_name + ' - ' + t_schema_name,
                'project_id': t_project_id,
                'unit_id': t_unit_id,
                'partner_id': t_entity_id,
                'company_id': t_company_id,
                'active': True,
                'stage_id': t_stage_id,
            }
            res = self.env['project.task'].create(vals)

            # crea work
            vals_work = {
                'user_id': self._uid,
                'task_id': res.id,
                'type_id': t_type.id,
                'unit_id': t_unit_id,
            }
            self.env['project.task.work'].create(vals_work)

            # log
            datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
            vals = {'work_id': self.id,
                    'doclite_action_type': 'create_maintenance_fee_tasks',
                    'project_task_id': res.id,
                    'exec_date': datetime_today,
                    'user_id': self._uid,
                    }
            self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_create_maintenance_fee_offer(self):

        # recupera dati
        t_account_analytic_id = self.project_id.analytic_account_id and self.project_id.analytic_account_id.id or None
        t_task_id = self.task_id and self.task_id.id or None
        t_date = fields.Date.context_today(self)
        t_partner_id = self.project_id.partner_id and self.project_id.partner_id.id or None
        t_partner_name = self.project_id.partner_id and self.project_id.partner_id.name or ''

        # TODO aggiungere controllo che partner sia un cliente?
        t_fiscal_position = None
        t_payment_term_id = None
        t_pricelist_id = None
        if t_partner_id:
            customer_address = self.project_id.partner_id.address_get(['default'])
            customer = self.env['res.partner'].browse(t_partner_id)

            t_pricelist_id = customer.property_product_pricelist.id
            t_fiscal_position = customer.property_account_position and customer.property_account_position.id or False
            t_payment_term_id = customer.property_payment_term.id or False

#        t_department_id = self.project_id.analytic_account_id.department_id and self.project_id.analytic_account_id.department_id.id or None
        t_department_nick = self.project_id.analytic_account_id.department_id and self.project_id.analytic_account_id.department_id.department_nick or ''

        # crea preventivo cliente
        vals = {'name': '/',
                'task_id': t_task_id,
                'project_id': t_account_analytic_id,
                'date_order': t_date,
                'partner_id': t_partner_id,
                'partner_invoice_id': customer_address and customer_address['default'] or None,
                'partner_shipping_id': customer_address and customer_address['default'] or None,
                'pricelist_id': t_pricelist_id,
                'payment_term_id': t_payment_term_id,
                'fiscal_position': t_fiscal_position,
                'origin': '',  # TODO
                'picking_policy': 'direct',  # TODO
                'order_policy': 'manual',  # TODO
                }

        t_product_id = self.type_id.product_maintenance_fee_id and self.type_id.product_maintenance_fee_id.id or None
        t_product_name = self.type_id.product_maintenance_fee_id and self.type_id.product_maintenance_fee_id.name or None

        product_uom = None
        try:
            # TODO
            product_uom = self.env['ir.model.data'].get_object_reference('product', 'product_uom_day')
        except ValueError:
            pass

        if product_uom:
            product_uom = product_uom[1]

        user_company_data = self.env['res.users'].browse(self._uid).company_id
        t_price_min = user_company_data.price_min
        t_fee_year = user_company_data.fee_year
        t_fee_year_small_lab = user_company_data.fee_year_small_lab
        t_price_fixed_lab = user_company_data.price_fixed_lab
        t_price_fixed_mer = user_company_data.price_fixed_mer

        line_vals = self.env['sale.order.line'].product_id_change(
            False, t_product_id, qty=1.0, uom=product_uom,
            qty_uos=1.0, uos=product_uom, name=t_product_name,
            partner_id=t_partner_id, lang=False, update_tax=True,
            date_order=time.strftime('%Y-%m-%d'))['value']

        line_vals.update({'name': t_product_name,
                          'tax_id': [[6, False, line_vals['tax_id']]],
                          'account_analytic_id': t_account_analytic_id,
                          })

        price = 0.0
        if t_department_nick == 'DC':
            # prezzo calcolato in base all'anno precedente di corresponsione:
            #     * se non accreditati, in base a valori in accreditation.group.charges
            #     * se già accreditati, in base a valori in accreditation.invoiced.schema

            datetime_today = datetime.strptime(t_date, DF)
            t_year = int(datetime_today.strftime("%Y")) - 1
            domain = [
                ('customer_id', '=', t_partner_id),
                ('year', '=', str(t_year)),
            ]
            invoiced_schemas = self.env['accreditation.invoiced.schema'].search(domain)
            if not invoiced_schemas:
                raise except_orm(_('Errore!'),
                                 _("Impossibile recuperare il fatturato dell'anno precedente per il Cliente %s!") % t_partner_name)
            invoiced_prev_year = 0.0
            for schema in invoiced_schemas:
                invoiced_prev_year += schema.invoiced_amount or 0.0
            domain = [
                ('invoiced_from', '<=', invoiced_prev_year),
                ('invoiced_to', '>', invoiced_prev_year),
            ]
            schema_group = self.env['accreditation.group.charges'].search(domain, limit=1)
            if not schema_group:
                raise except_orm(_('Errore!'),
                                 _('Manca la configurazione degli scaglioni!'))
            price = schema_group.percentage * invoiced_prev_year

            if price < t_price_min:
                price = t_price_min

        elif t_department_nick == 'DL':
            # Preventivo con quota annua
            domain = [
                ('customer_id', '=', t_partner_id),
            ]
            lab = self.env['accreditation.small.lab'].search(domain, limit=1)
            if not lab:
                raise except_orm(_('Errore!'),
                                 _('Manca la configurazione per il Cliente %s!') % t_partner_name)
            price = t_fee_year
            if lab.is_small_lab:
                price = t_fee_year_small_lab  # se piccolo laboratorio, tariffa più bassa

        elif t_department_nick == 'DT':
            # TODO
            price = t_price_fixed_lab  # TODO quota fissa per ogni laboratorio accreditato
            price = t_price_fixed_mer  # TODO quota fissa per ogni settore metrologico accreditato

        line_vals.update({'price_unit': price,
                          })

        vals.update({'order_line': [(0, 0, line_vals)], })

        res = self.env['sale.order'].create(vals)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'create_sale_quotation',
                'sale_order_id': res.id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        if t_department_nick == 'DC':
            # creazione fattura a saldo, collegata con il preventivo

            vals = self.env['account.invoice'].onchange_partner_id(
                'out_invoice', t_partner_id)['value']
            vals['partner_id'] = t_partner_id

            line_vals = {'name': t_product_name,
                         'account_analytic_id': t_account_analytic_id,
                         }

            vals.update({'invoice_line': [(0, 0, line_vals)], })

            res = self.env['account.invoice'].create(vals)

            # log
            datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
            vals = {'work_id': self.id,
                    'doclite_action_type': 'create_advance_invoice',
                    'advance_invoice_id': res.id,
                    'exec_date': datetime_today,
                    'user_id': self._uid,
                    }
            self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_del_obtained_accreditation(self):

        # imposta campo obtained nell'ente
        self.project_id.partner_id.obtained = False

        # imposta campo Data fine accreditamento della pratica
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        self.project_id.accreditation_expiry_date = datetime_today

        # log
        vals = {'work_id': self.id,
                'doclite_action_type': 'del_obtained_accreditation',
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.one
    def do_get_accreditation_test(self):

        test_list = []

        for test_data in self.project_id.test_ids:
            if test_data.id not in test_list:
                test_list.append(test_data.id)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'get_accreditation_test',
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        if test_list:
            result = self.env['ir.model.data'].get_object_reference('project_accredia',
                                                                    'view_accreditation_test_form')
            view_id = result and result[1] or False

            return {'domain': "[('id','in', ["+','.join(map(str, test_list))+"])]",
                    'name': _("Prove Accreditate"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'accreditation.test',
                    'type': 'ir.actions.act_window',
                    'views': [(False, 'tree'), (view_id, 'form')],
                    }
        return True

    @api.one
    def do_create_child_project(self):

        # recupera dati
        t_analytic_account_id = self.project_id and self.project_id.analytic_account_id and self.project_id.analytic_account_id.id or None
        t_user_id = self.project_id and self.project_id.user_id and self.project_id.user_id.id or None
        t_partner_id = self.project_id and self.project_id.partner_id and self.project_id.partner_id.id or None
        t_certificate_number = self.project_id and self.project_id.certificate_number or None
        t_accreditation_due_date = self.project_id and self.project_id.accreditation_due_date or None
        t_department_id = self.type_id.child_project_department_id and self.type_id.child_project_department_id.id or None
        t_type_id = self.type_id.child_project_type_id and self.type_id.child_project_type_id.id or None
        t_name = self.project_id and self.project_id.name or None
        t_cab_code = self.project_id and self.project_id.cab_code or None

        # crea pratica collegata
        ctx = dict(self._context)
        ctx.update({'analytic_project_copy': True,
                    'copy': True,
                    })
        dict_default = {'state': 'open',
                        'accreditation_project_type': t_type_id,
                        'department_id': t_department_id,
                        'parent_id': t_analytic_account_id,
                        'user_id': t_user_id,
                        'partner_id': t_partner_id,
                        'certificate_number': t_certificate_number,
                        'accreditation_due_date': t_accreditation_due_date,
                        'child_ids': [],
                        'name': t_name,
                        'cab_code': t_cab_code,
                        'team_ids': [(6, 0, [team.id for team in self.project_id.team_ids])],
                        }
        template_data = self.type_id.child_project_template_id
        project_obj = self.pool['project.project']
        new_project_id = project_obj.copy(self._cr, self._uid,
                                          template_data.id,
                                          default=dict_default,
                                          context=ctx)

        # log
        datetime_today = datetime.strptime(fields.Date.context_today(self), DF)
        vals = {'work_id': self.id,
                'doclite_action_type': 'create_child_project',
                'child_project_id': new_project_id,
                'exec_date': datetime_today,
                'user_id': self._uid,
                }
        self.env['accreditation.task.work.log'].create(vals)

        return True

    @api.multi
    def do_action_launch_wizard(self):
        if self.type_id.set_obtained_accreditation or self.type_id.del_obtained_accreditation:
            context = {}
            if self.type_id.set_obtained_accreditation:
                context = {'set_obtained_accreditation' :True }
            if self.type_id.del_obtained_accreditation:
                context = {'del_obtained_accreditation' :True }
            mod_obj = self.pool.get('ir.model.data')
            model, wizard_id = self.env['ir.model.data'].get_object_reference('project_action_accredia', 'view_project_task_wizard')
            return {
                'name': _("Set Date"),
                'view_mode': 'form',
                'view_id': wizard_id,
                'res_model': 'project.task.wizard',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': context
            }
        else :
            return self.do_action()


    @api.multi
    def do_action(self):

        t_date = fields.Date.context_today(self)
        self.exec_date = t_date
        res = None
        if self.type_id:
            # Controlli iniziali
            if self.type_id.req_supervision and not self.task_id.req_supervision_days:
                raise except_orm(_('Errore!'),
                                 _('Il campo Giorni per Sorveglianza deve essere impostato nell\'attività!'))

            # Esecuzione Azioni
            if self.type_id.create_audit:
                res = self.do_create_audit()

            if self.type_id.create_line_to_invoice:
                res = self.do_create_line_to_invoice()

            if self.type_id.create_quotation:
                res = self.do_create_quotation()

            if self.type_id.create_purchase_requisition:
                res = self.do_create_purchase_requisition()

            if self.type_id.create_sale_quotation:
                res = self.do_create_sale_quotation()

            if self.type_id.update_agenda:
                res = self.do_update_agenda()

            if self.type_id.accreditation_request_generation:
                res = self.do_accreditation_request_generation()

            if self.type_id.create_child_project:
                res = self.do_create_child_project()

            if self.type_id.get_accreditation_test:
                res = self.do_get_accreditation_test()

            if self.type_id.create_maintenance_fee_tasks:
                self.do_create_maintenance_fee_tasks()

            if self.type_id.create_maintenance_fee_offer:
                self.do_create_maintenance_fee_offer()

            # doclite
            if self.type_id.doclite_action:
                res = self.do_doclite_action()

            # Aggiorno data inizio e fine
            if not self.date:
                self.date = t_date
            if not self.date_end:
                self.date_end = t_date

        return res

    @api.one
    def do_not_action(self):

        t_date = fields.Date.context_today(self)
        self.date = t_date
        self.date_end = t_date
        self.exec_date = t_date

    @api.multi
    def open_to_plan_phase_ids(self):
        self.ensure_one()
        if self.fnct_to_plan_phase_ids:
            result = self.env['ir.model.data'].get_object_reference('project_long_term_accredia',
                                                                    'view_project_phase_form')
            view_id = result and result[1] or False

            ctx = self._context.copy()
            t_ids = self.fnct_to_plan_phase_ids.ids
            return {'domain': "[('id','in', ["+','.join(map(str, t_ids))+"])]",
                    'name': _("Audit da pianificare"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'project.phase',
                    'type': 'ir.actions.act_window',
                    'context': ctx,
                    'views': [(False, 'tree'), (view_id, 'form')],
                    }
        return True

    @api.multi
    def _compute_to_plan_phase_ids(self):
        self.ensure_one()
        for data in self.log_ids:
            if data.to_plan_project_id:
                phases = self.env['project.phase'].search(
                    [('project_id', '=', data.to_plan_project_id.id),
                     ('audit_task_type', '=', 'foreseen')
                     ])
                self.fnct_to_plan_phase_ids = phases

    @api.one
    def _compute_results(self):
        self.fnct_phase_id = None
        self.fnct_analytic_line_id = None
        self.fnct_action_url = ''
        self.fnct_purchase_order_id = None
        self.fnct_purchase_requisition_id = None
        self.fnct_sale_order_id = None
        self.fnct_advance_invoice_id = None
        self.fnct_meeting_id = None
        self.fnct_request_id = None
        self.fnct_project_id = None
        for data in self.log_ids:
            if data.phase_id:
                self.fnct_phase_id = data.phase_id
            if data.analytic_line_id:
                self.fnct_analytic_line_id = data.analytic_line_id
            if data.action_url:
                self.fnct_action_url = data.action_url
            if data.purchase_order_id:
                self.fnct_purchase_order_id = data.purchase_order_id
            if data.purchase_requisition_id:
                self.fnct_purchase_requisition_id = data.purchase_requisition_id
            if data.sale_order_id:
                self.fnct_sale_order_id = data.sale_order_id
            if data.advance_invoice_id:
                self.fnct_advance_invoice_id = data.advance_invoice_id
            if data.meeting_id:
                self.fnct_meeting_id = data.meeting_id
            if data.request_id:
                self.fnct_request_id = data.request_id
            if data.child_project_id:
                self.fnct_project_id = data.child_project_id

    @api.multi
    def _compute_project_task_ids(self):
        self.ensure_one()
        for data in self.log_ids:
            if data.project_task_id:
                self.fnct_project_task_ids += data.project_task_id

    log_ids = fields.One2many('accreditation.task.work.log', 'work_id', 'Log Azioni')
    fnct_phase_id = fields.Many2one(comodel_name='project.phase', string='Audit', compute='_compute_results')
    fnct_to_plan_phase_ids = fields.One2many(comodel_name='project.phase', string='Audit da pianificare', compute='_compute_to_plan_phase_ids')
    fnct_analytic_line_id = fields.Many2one(comodel_name='account.analytic.line', string='Riga Analitica', compute='_compute_results')
    fnct_action_url = fields.Char(string='Link', compute='_compute_results')
    fnct_purchase_order_id = fields.Many2one(comodel_name='purchase.order', string='Ordine Acquisto', compute='_compute_results')
    fnct_project_task_ids = fields.One2many(comodel_name='project.task', string='Attività Diritti Mantenimento', compute='_compute_project_task_ids')
    fnct_purchase_requisition_id = fields.Many2one(comodel_name='purchase.requisition', string='Richiesta Acquisto', compute='_compute_results')
    fnct_sale_order_id = fields.Many2one(comodel_name='sale.order', string='Preventivo', compute='_compute_results')
    fnct_advance_invoice_id = fields.Many2one(comodel_name='account.invoice', string='Fattura Acconto', compute='_compute_results')
    fnct_meeting_id = fields.Many2one(comodel_name='calendar.event', string='Meeting', compute='_compute_results')
    fnct_request_id = fields.Many2one(comodel_name='accreditation.request', string='Richiesta', compute='_compute_results')
    fnct_project_id = fields.Many2one(comodel_name='project.project', string='Pratica', compute='_compute_results')
