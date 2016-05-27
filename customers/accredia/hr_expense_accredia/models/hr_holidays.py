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
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    def _get_expense_number(self):
        self.expense_number = None
        if self.task_id and self.task_id.expense_ids:
            for expense_data in self.task_id.expense_ids:
                self.expense_number = expense_data.expense_number
                break

    @api.one
    def _get_expense_id(self):
        self.expense_id = None
        if self.task_id and self.task_id.expense_ids:
            for expense_data in self.task_id.expense_ids:
                self.expense_id = expense_data
                break

    @api.onchange('task_id')
    def onchange_task(self):
        self.expense_id = None
        self.name = 'Richiesta di Missione '
        if self.task_id:
            if self.task_id.expense_ids:
                for expense_data in self.task_id.expense_ids:
                    self.expense_id = expense_data
                    break
            self.name += self.task_id.description or ''

    def onchange_employee(self, cr, uid, ids, employee_id):
        res = super(HrHolidays, self).onchange_employee(cr, uid, ids, employee_id)
        res['value']['task_id'] = None
        res['value']['partner_id'] = None
        res['value']['user_id'] = None

        if employee_id:
            employee_obj = self.pool.get('hr.employee')
            employee_data = employee_obj.browse(cr, uid, employee_id)
            if employee_data.user_id:
                res['value']['user_id'] = employee_data.user_id.id
                res['value']['task_id'] = None
                res['value']['partner_id'] = employee_data.user_id.partner_id.id

        return res

    def onchange_type(self, cr, uid, ids, holiday_type, context=None):
        result = super(HrHolidays, self).onchange_type(cr, uid, ids, holiday_type)
        if holiday_type == 'mission':
            type_ids = self.pool.get('hr.holidays.status').search(cr, uid, [('name', 'ilike', 'Missione')], limit=1)
            if type_ids:
                result['value'] = {
                    'holiday_status_id': type_ids[0]
                }
        return result

    def _get_default_currency(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.currency_id.id

    task_id = fields.Many2one('project.task', 'Riferimento')
    project_id = fields.Many2one(related='task_id.project_id',
                                 comodel_name="project.project",
                                 store=False, string="Pratica", required=False, readonly=True)
    user_id = fields.Many2one(related='employee_id.user_id', comodel_name="res.users",
                              store=False, string="User", required=False, readonly=True)
    partner_id = fields.Many2one(related='employee_id.user_id.partner_id',
                                 store=False,
                                 readonly=True,
                                 comodel_name='res.partner',
                                 string='Persona Fisica')

    km_expected = fields.Float(string='KM Previsti')
    expense_number = fields.Char(compute='_get_expense_number', string='Num. Nota Spese')
    expense_id = fields.Many2one(compute='_get_expense_id', comodel_name='hr.expense.expense', string='Num. Nota Spese')
    date_valid = fields.Date('Validation Date', select=True, help="Date of the acceptation of the authorization.")
    holiday_type = fields.Selection([('mission', 'Missione'),
                                     ('employee', 'By Employee'),
                                     ('category', 'By Employee Tag')],
                                    'Allocation Mode',
                                    readonly=True,
                                    states={'draft': [('readonly', False)],
                                            'confirm': [('readonly', False)]},
                                    help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category',
                                    required=True)
    line_ids = fields.One2many('hr.holidays.line', 'holidays_id', string='Holiday Lines')

    own_car_use = fields.Boolean('Autorizz. Propria Vettura')
    cash_advance = fields.Float('Anticipo Contante (Euro)', digits_compute=dp.get_precision('Account'))
    cash_currency_id = fields.Many2one('res.currency', 'Valuta Anticipo Contante')
    note = fields.Text('Note')
    holiday_status_id = fields.Many2one('hr.holidays.status', 'Leave Type', required=False, readonly=False,
                                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    date_doc_delivery = fields.Datetime('Consegna documenti')
    create_date = fields.Date('Data Richiesta')
    secretary_executed = fields.Boolean('Eseguito Segreteria')

    _defaults = {
        'holiday_type': 'mission',
        'cash_currency_id': _get_default_currency,
    }

    _sql_constraints = [
        ('type_value', "CHECK( (holiday_type='mission' AND department_id IS NOT NULL) or (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))", 
         "Manca l'impiegato o la categoria dell'impiegato per questa richiesta. Per favore assicurati che l'impiegato sia collegato all'utente."),
    ]

    @api.model
    def create(self, vals):

        if 'task_id' in vals and vals['task_id'] and 'employee_id' in vals and vals['employee_id']:
            task = self.env['project.task'].browse(vals['task_id'])
            for holiday in task.holiday_ids:
                if holiday.employee_id and holiday.employee_id.id == vals['employee_id']:
                    raise except_orm(_('Errore!'),
                                     _("Per questo Audit esiste già una richiesta di Missione!"))

        t_date_from = None
        t_date_to = None
        t_employee_id = None
        if 'date_from' in vals and vals['date_from']:
            t_date_from = vals['date_from']
        if 'date_to' in vals and vals['date_to']:
            t_date_to = vals['date_to']
        if 'employee_id' in vals and vals['employee_id']:
            t_employee_id = vals['employee_id']

        if t_date_from and t_date_to and t_employee_id:
            holidays = self.env['hr.holidays'].search([('date_from', '<=', t_date_to),
                                                       ('date_to', '>=', t_date_from),
                                                       ('employee_id', '=', t_employee_id)],
                                                      limit=1)
            if holidays:
                raise except_orm(_('Errore!'),
                                 _("Non puoi avere due richieste che si sovrappongono nello stesso giorno!"))

        res = super(HrHolidays, self).create(vals)

        return res

    @api.multi
    def write(self, vals):

        for data in self:
            t_task_id = 'task_id' in vals and vals['task_id'] or None
            t_date_from = data.date_from
            t_date_to = data.date_to
            t_employee_id = data.employee_id and data.employee_id.id or None

            if 'date_from' in vals and vals['date_from']:
                t_date_from = vals['date_from']
            if 'date_to' in vals and vals['date_to']:
                t_date_to = vals['date_to']
            if 'employee_id' in vals and vals['employee_id']:
                t_employee_id = vals['employee_id']

            if t_task_id or t_employee_id:
                if not t_task_id:
                    t_task_id = data.task_id and data.task_id.id or None
                if not t_employee_id:
                    t_employee_id = data.employee_id and data.employee_id.id or None

            if t_task_id and t_employee_id:
                t_task_data = self.env['project.task'].browse(t_task_id)
                '''
                for t_holiday in t_task_data.holiday_ids:
                    if t_holiday.employee_id and t_holiday.employee_id.id == t_employee_id:
                        raise except_orm(_('Errore!'),
                                         _("Per questo Audit esiste già una richiesta di Missione!"))
                '''

            if t_date_from and t_date_to and t_employee_id:
                holidays = self.env['hr.holidays'].search([('date_from', '<=', t_date_to),
                                                           ('date_to', '>=', t_date_from),
                                                           ('employee_id', '=', t_employee_id),
                                                           ('id', '<>', data.id)],
                                                          limit=1)
                if holidays:
                    raise except_orm(_('Errore!'),
                                     _("Non puoi avere due richieste che si sovrappongono nello stesso giorno!"))

        res = super(HrHolidays, self).write(vals)

        return res

    def holidays_validate(self, cr, uid, ids, context=None):
        res = super(HrHolidays, self).holidays_validate(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'date_valid': time.strftime('%Y-%m-%d')})
        return res

    def holidays_confirm(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.department_id and record.department_id.parent_id and record.department_id.parent_id.manager_id and record.department_id.parent_id.manager_id.user_id:
                self.message_subscribe_users(cr, uid, [record.id], user_ids=[record.department_id.parent_id.manager_id.user_id.id], context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'})

    @api.multi
    @api.depends('state', 'date_valid', 'double_validation', 'manager_id', 'manager_id2')
    def name_get(self):
        res = []
        for record in self:
            if record.state == 'validate' and record.date_valid:
                t_manager = record.manager_id and record.manager_id.name or ''
                if record.double_validation:
                    t_manager = record.manager_id2 and record.manager_id2.name or ''
                name = 'N.: ' + str(record.id) + ' del ' + record.date_valid + ' (' + t_manager + ')'
                res.append((record.id, name))
            else:
                name = 'N.: ' + str(record.id)
                res.append((record.id, name))
        return res
