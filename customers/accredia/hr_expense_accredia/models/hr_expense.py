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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


class hr_expense(orm.Model):
    _inherit = 'hr.expense.expense'

    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(hr_expense, self).move_line_get_item(cr, uid, line, context=context)
        res['task_id'] = line.task_id and line.task_id.id or False
        res['expense_line_id'] = line.id or False
        return res

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(hr_expense, self).line_get_convert(cr, uid, x, part, date, context=context)
        res['task_id'] = x.get('task_id', False)
        res['expense_line_id'] = x.get('expense_line_id', False)
        return res

    def _get_holiday_id(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = None
            for t_holiday_data in rec.holiday_ids:
                if t_holiday_data.partner_id and rec.user_id and rec.user_id.partner_id:
                    if t_holiday_data.partner_id.id == rec.user_id.partner_id.id:
                        result[rec.id] = t_holiday_data.id
                        break
        return result

    def _get_own_car_use(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            result[rec.id] = False
            for t_holiday_data in rec.holiday_ids:
                if t_holiday_data.partner_id and rec.user_id and rec.user_id.partner_id:
                    result[rec.id] = t_holiday_data.own_car_use
                    if t_holiday_data.partner_id.id == rec.user_id.partner_id.id:
                        break
        return result

    def onchange_task(self, cr, uid, ids, task_id, user_id, context=None):
        if not task_id:
            return {}
        t_city = None
        data = self.pool.get('project.task').browse(cr, uid, task_id)
        if data and data.project_id and data.project_id.partner_id:
            t_city = data.project_id.partner_id.city
        if data.unit_id and data.unit_id.location_id:
            t_city = data.unit_id.location_id.city

        partner_id = None
        if user_id:
            partner_id = self.pool.get('res.users').browse(cr, uid, user_id).partner_id.id

        t_mission_id = None
        t_cash_advance = 0.0
        t_cash_currency = None
        t_own_car_use = False
        if data and data.holiday_ids:
            for t_holiday_data in data.holiday_ids:
                if t_holiday_data.partner_id and partner_id and t_holiday_data.partner_id.id == partner_id:

                    t_mission_id = t_holiday_data.id
                    t_cash_advance = t_holiday_data.cash_advance
                    t_cash_currency = t_holiday_data.cash_currency_id and t_holiday_data.cash_currency_id.id or None
                    t_own_car_use = t_holiday_data.own_car_use

        return {'value': {'city': t_city,
                          'holiday_id': t_mission_id,
                          'amount_deposit': t_cash_advance,
                          'cash_currency_id': t_cash_currency,
                          'own_car_use': t_own_car_use,
                          }}

    def action_receipt_create(self, cr, uid, ids, context=None):
        '''
        main function that is called when trying to create the accounting entries related to an expense
        '''
        move_obj = self.pool.get('account.move')
        for exp in self.browse(cr, uid, ids, context=context):

            if not exp.user_id:
                raise orm.except_orm(_('Error!'), _('Nessun utente specificato.'))

            if not exp.user_id.partner_id:
                raise orm.except_orm(_('Error!'), _('Nessun partner specificato.'))

            if exp.employee_id:
                if not exp.employee_id.address_home_id:
                    raise orm.except_orm(_('Error!'), _('The employee must have a home address.'))
                if not exp.employee_id.address_home_id.property_account_payable.id:
                    raise orm.except_orm(_('Error!'), _('The employee must have a payable account set on his home address.'))

            company_currency = exp.company_id.currency_id.id
            diff_currency_p = exp.currency_id.id != company_currency

            # create the move that will contain the accounting entries
            move_id = move_obj.create(cr, uid, self.account_move_get(cr, uid, exp.id, context=context), context=context)

            # one account.move.line per expense line (+taxes..)
            eml = self.move_line_get(cr, uid, exp.id, context=context)

            # create one more move line, a counterline for the total on payable account
            total, total_currency, eml = self.compute_expense_totals(cr, uid, exp, company_currency, exp.name, eml, context=context)

            acc = exp.user_id.partner_id and exp.user_id.partner_id.property_account_payable and exp.user_id.partner_id.property_account_payable.id or None
            if exp.employee_id:
                acc = exp.employee_id.address_home_id.property_account_payable.id
            if not acc:
                raise orm.except_orm(_('Error!'), _('Nessun conto payable definito per questo partner.'))
            eml.append({'type': 'dest',
                        'name': '/',
                        'price': total,
                        'account_id': acc,
                        'date_maturity': exp.date_confirm,
                        'amount_currency': diff_currency_p and total_currency or False,
                        'currency_id': diff_currency_p and exp.currency_id.id or False,
                        'ref': exp.name
                        })

            # convert eml into an osv-valid format
            t_address_home_id = exp.employee_id and exp.employee_id.address_home_id or exp.user_id.partner_id
            lines = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, t_address_home_id, exp.date_confirm, context=context)), eml)
            journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
            # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
            if journal_id.entry_posted:
                move_obj.button_validate(cr, uid, [move_id], context)
            move_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
            self.write(cr, uid, ids, {'account_move_id': move_id, 'state': 'done'}, context=context)
        return True

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):
        department_id = False
        res = {'value': {}}
        if employee_id:
            employee_obj = self.pool.get('hr.employee')
            employee_data = employee_obj.browse(cr, uid, employee_id, context=context)
            department_id = employee_data.department_id and employee_data.department_id.id or None
            res = {'value': {'department_id': department_id}}
            res['value']['task_id'] = None
            res['value']['user_id'] = employee_data.user_id and employee_data.user_id.id or None
            res['domain'] = {}
            res['domain']['task_id'] = []
            res['domain']['task_id'].append(('phase_id', '!=', False))

            if employee_data.user_id:
                t_user_id = employee_data.user_id.id
                res['domain']['task_id'].append(('task_team_ids.user_id', '=', t_user_id))
            res['domain']['task_id'] = str(res['domain']['task_id'])
        return res

    def onchange_user_id(self, cr, uid, ids, user_id, context=None):
        # TODO da rivedere
        res = {'value': {'department_id': None}}
        res['value']['task_id'] = None
        res['value']['employee_id'] = None
        res['domain'] = {}
        res['domain']['task_id'] = []
        res['domain']['task_id'].append(('phase_id', '!=', False))
        if user_id:
            user_obj = self.pool.get('res.users')
            user_data = user_obj.browse(cr, uid, user_id, context=context)
            partner_data = user_data.partner_id

            res['value']['department_id'] = partner_data.department_id and partner_data.department_id.id or None
            res['domain']['task_id'].append(('task_team_ids.user_id', '=', user_data.id))

            for employee_data in user_data.employee_ids:
                res['value']['employee_id'] = employee_data.id
                res['value']['department_id'] = employee_data.department_id and employee_data.department_id.id or None
                break
        res['domain']['task_id'] = str(res['domain']['task_id'])
        return res

    def onchange_department_id(self, cr, uid, ids, department_id, context=None):
        value = {'journal_id': None, }
        if department_id:
            data = self.pool.get('hr.department').browse(cr, uid, department_id)
            if data and data.expense_journal_id:
                value = {'journal_id': data.expense_journal_id.id,
                         }

        return {'value': value}

    def onchange_holiday_id(self, cr, uid, ids, holiday_id):
        value = {'own_car_use': None, }
        if holiday_id:
            data = self.pool.get('hr.holidays').browse(cr, uid, holiday_id)
            if data and data.own_car_use:
                value = {'own_car_use': data.own_car_use,
                         'amount_deposit': data.cash_advance,
                         'cash_currency_id': data.cash_currency_id and data.cash_currency_id.id or None,
                         }

        return {'value': value}

    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for expense in self.browse(cr, uid, ids, context=context):
            res[expense.id] = {
                'amount_paid': 0.0,
                'amount_to_refund': 0.0
            }
            for line in expense.line_ids:
                if line.already_paid:
                    res[expense.id]['amount_paid'] += line.total_amount
            res[expense.id]['amount_to_refund'] = expense.amount - expense.amount_deposit - res[expense.id]['amount_paid']
        return res


    def move_line_get(self, cr, uid, expense_id, context=None):
        #E' stato ridefinito il metodo base, escludendo la parte relativa alle tasse
        res = []
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        if context is None:
            context = {}
        exp = self.browse(cr, uid, expense_id, context=context)
        company_currency = exp.company_id.currency_id.id

        for line in exp.line_ids:
            mres = self.move_line_get_item(cr, uid, line, context)
            if not mres:
                continue
            res.append(mres)

            #Calculate tax according to default tax on product
            taxes = []
            #Taken from product_id_onchange in account.invoice
            if line.product_id:
                fposition_id = False
                fpos_obj = self.pool.get('account.fiscal.position')
                fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False
                product = line.product_id
                taxes = product.supplier_taxes_id
                #If taxes are not related to the product, maybe they are in the account
                if not taxes:
                    a = product.property_account_expense.id #Why is not there a check here?
                    if not a:
                        a = product.categ_id.property_account_expense_categ.id
                    a = fpos_obj.map_account(cr, uid, fpos, a)
                    taxes = a and self.pool.get('account.account').browse(cr, uid, a, context=context).tax_ids or False
            if not taxes:
                continue
        return res

    def action_move_create(self, cr, uid, ids, context=None):
        #Se esiste il dipendente, richiamo la funzione base, altrimenti se non esiste il dipendente,
        #reperisco il partner dall'utente e riscrivo la funzione base togliendo il controllo
        exp_obj = self.browse(cr, uid, ids, context=context)
        if exp_obj.employee_id:
            return super(hr_expense, self).action_move_create(cr, uid, ids, context)
        else:
            #Ora riscrivo la funzione base, omettendo il controllo
            move_obj = self.pool.get('account.move')
            for exp in self.browse(cr, uid, ids, context=context):
                if not exp.user_id.partner_id.property_account_payable.id:
                    raise osv.except_osv(_('Error!'), _('The user must have a payable account set on his home address.'))
                company_currency = exp.company_id.currency_id.id
                diff_currency_p = exp.currency_id.id <> company_currency

                #create the move that will contain the accounting entries
                move_id = move_obj.create(cr, uid, self.account_move_get(cr, uid, exp.id, context=context), context=context)

                #one account.move.line per expense line (+taxes..)
                eml = self.move_line_get(cr, uid, exp.id, context=context)

                #create one more move line, a counterline for the total on payable account
                total, total_currency, eml = self.compute_expense_totals(cr, uid, exp, company_currency, exp.name, eml, context=context)
                acc = exp.user_id.partner_id.property_account_payable.id
                eml.append({
                        'type': 'dest',
                        'name': '/',
                        'price': total,
                        'account_id': acc,
                        'date_maturity': exp.date_confirm,
                        'amount_currency': diff_currency_p and total_currency or False,
                        'currency_id': diff_currency_p and exp.currency_id.id or False,
                        'ref': exp.name
                        })

                #convert eml into an osv-valid format
                lines = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, exp.user_id.partner_id, exp.date_confirm, context=context)), eml)
                journal_id = move_obj.browse(cr, uid, move_id, context).journal_id
                # post the journal entry if 'Skip 'Draft' State for Manual Entries' is checked
                if journal_id.entry_posted:
                    move_obj.button_validate(cr, uid, [move_id], context)
                move_obj.write(cr, uid, [move_id], {'line_id': lines}, context=context)
                self.write(cr, uid, ids, {'account_move_id': move_id, 'state': 'done'}, context=context)
            return True


    _columns = {
        'name': fields.char('Description',
                            size=128,
                            required=False,
                            readonly=True,
                            states={'draft':[('readonly',False)],
                                    'confirm':[('readonly',False)]}),
        'task_id': fields.many2one('project.task',
                                   'Riferimento',
                                   readonly=True,
                                   states={'draft':[('readonly',False)],
                                           'confirm':[('readonly',False)]}),
        'project_id': fields.related('task_id',
                                     'project_id',
                                     type="many2one",
                                     relation="project.project",
                                     store=False,
                                     string="Pratica",
                                     required=False,
                                     readonly=True),
        'amount_deposit': fields.float('Importo Anticipo',
                                       digits_compute=dp.get_precision('Account'),
                                       readonly=True,
                                       states={'draft':[('readonly',False)],
                                               'confirm':[('readonly',False)]}),
        'cash_currency_id': fields.many2one('res.currency',
                                            'Valuta Anticipo',
                                            readonly=True,
                                            states={'draft':[('readonly',False)],
                                                    'confirm':[('readonly',False)]}),
        'amount_paid': fields.function(_amount_all,
                                       digits_compute=dp.get_precision('Account'),
                                       string='Già pagate',
                                       store=True,
                                       multi='all'),
        'amount_to_refund': fields.function(_amount_all,
                                            digits_compute=dp.get_precision('Account'),
                                            string='Da rimborsare',
                                            store=True,
                                            multi='all'),
        'city': fields.char('Luogo',
                            size=120,
                            readonly=True,
                            states={'draft':[('readonly',False)],
                                    'confirm':[('readonly',False)]}),
        'expense_number': fields.char('Progressivo',
                                      size=120,
                                      readonly=True,
                                      states={'draft':[('readonly',False)],
                                              'confirm':[('readonly',False)]}),
        'user_id': fields.many2one("res.users",
                                   string="Utente",
                                   required=True,
                                   readonly=True,
                                   states={'draft':[('readonly',False)],
                                           'confirm':[('readonly',False)]}),
        'currency_rate': fields.float('Tasso di cambio',
                                      digits=(12,6),
                                      readonly=True,
                                      states={'draft':[('readonly',False)],
                                              'confirm':[('readonly',False)]}),
        'holiday_ids': fields.related('task_id',
                                      'holiday_ids',
                                      type='one2many',
                                      relation='hr.holidays',
                                      readonly=True,
                                      store=False,
                                      string='Autorizzazioni'),
        'holiday_id': fields.function(_get_holiday_id,
                                      type='many2one',
                                      relation='hr.holidays',
                                      string='Autorizzazione alla missione',),
        'own_car_use': fields.function(_get_own_car_use,
                                      type='boolean',
                                      string='Autorizz. Propria Vettura'),
        'hidden': fields.char('Hidden', size=1),

        'employee_id': fields.many2one('hr.employee',   
                                       "Impiegato",
                                       required=False,
                                       readonly=True,
                                       states={'draft':[('readonly',False)],
                                               'confirm':[('readonly',False)]}),
        'note': fields.text('Note',
                            readonly=True,
                            states={'draft':[('readonly',False)],
                                    'confirm':[('readonly',False)],
                                    'accepted':[('readonly',False)]}),
        'account_move_id': fields.many2one('account.move',
                                           'Ledger Posting',
                                           readonly=True,
                                           states={'draft':[('readonly',False)],
                                                   'confirm':[('readonly',False)],
                                                   'accepted':[('readonly',False)]}),
        }

    _defaults = {
        'currency_rate': 1.0,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'res.users', context=c),
    }

    def button_reset_amounts(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        # Update the stored value (fields.function), so we write to trigger recompute
        self.write(cr, uid, ids, {'hidden': ''}, context=context)
        return True

    def create(self, cr, user, vals, context=None):
        if context is None:
            context = {}

        if 'employee_id' in vals and vals['employee_id']:
            if 'task_id' in vals and vals['task_id']:
                data = self.pool.get('project.task').browse(cr, user, vals['task_id'])
                for t_holiday_data in data.holiday_ids:
                    if t_holiday_data.partner_id and data.partner_id:
                        if t_holiday_data.partner_id.id == data.partner_id.id:
                            break
                            raise orm.except_orm(_('Errore!'),
                                                 _("Manca l'autorizzazione alla missione per questo dipendente!"))

        if 'department_id' not in vals or not vals['department_id']:
            raise orm.except_orm(_('Errore!'),
                                 _('Il campo dipartimento è obbligatorio!'))

        t_department_obj = self.pool.get('hr.department')
        t_department_data = t_department_obj.browse(cr, user, vals['department_id'])
        if not t_department_data.expense_sequence_id:
            raise orm.except_orm(_('Errore!'),
                                 _('La sequenza Spese nel Dipartimento %s è obbligatoria!') % (t_department_data.name))

        if not t_department_data.expense_journal_id:
            raise orm.except_orm(_('Errore!'),
                                 _('Il Sezionale Note Spese nel Dipartimento %s è obbligatorio!') % (t_department_data.name))

        vals['journal_id'] = t_department_data.expense_journal_id.id

        t_seq_id = t_department_data.expense_sequence_id.id
        sequence_obj = self.pool.get('ir.sequence')
        t_new_expense_number = sequence_obj.next_by_id(cr, user, t_seq_id)
        vals.update({'expense_number': t_new_expense_number, })

        res = super(hr_expense, self).create(cr, user, vals, context)

        return res

    def _expense_check(self, cr, uid, ids, context=None):
        for expense in self.browse(cr, uid, ids):
            if not expense.task_id:
                raise orm.except_orm(_('Errore!'),
                                     _('Il campo Riferimento (Audit) è obbligatorio!'))
            if expense.holiday_id and expense.holiday_id.state != 'validate':
                raise orm.except_orm(_('Errore!'),
                                     _("L'autorizzazione alla missione non è approvata!"))

            if expense.employee_id and not expense.holiday_id:
                raise orm.except_orm(_('Errore!'),
                                     _("Manca l'autorizzazione alla missione per questo dipendente!"))

            company_currency = expense.company_id.currency_id.id
            t_currencies = []
            for t_line in expense.line_ids:
                if t_line.currency_id and t_line.currency_id.id not in t_currencies:
                    if t_line.currency_id.id != company_currency:
                        t_currencies.append(t_line.currency_id.id)
            if len(t_currencies) >= 2:
                raise orm.except_orm(_('Errore!'),
                                     _('Non sono ammesse più valute estere!'))

    def expense_confirm(self, cr, uid, ids, context=None):
        # Submit to manager
        self._expense_check(cr, uid, ids, context)
        res = super(hr_expense, self).expense_confirm(cr, uid, ids, context)
        return res

    def expense_accept(self, cr, uid, ids, context=None):
        # Approva
        self._expense_check(cr, uid, ids, context)
        res = super(hr_expense, self).expense_accept(cr, uid, ids, context)
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        res = super(hr_expense, self).name_get(cr, uid, ids, context=context)

        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.expense_number:
                name = record.expense_number
            if record.state == 'accepted' or record.state == 'done' or record.state == 'paid':
                name = record.expense_number
                if record.expense_number and record.date:
                    name = record.expense_number + ' del ' + record.date
            res.append((record.id, name))
        return res
