# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Apulia Software S.r.l. (<info@apuliasoftware.it>)
#    All Rights Reserved
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

from openerp.osv import fields, osv, orm
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _


class account_asset_category(orm.Model):

    _inherit = 'account.asset.category'

    _columns = {
        'code': fields.char('Asset Category Code', size=20),
        'asset_type': fields.selection(
            (('M', 'Material asset'),
             ('I', 'Intangible asset'),
             ('P', 'Capital gain')),
            'Type Asset'),
        'ordinary_amortization': fields.float(
            'Ordinary Amortization',
            digits_compute=dp.get_precision('Account')),
        'amortization_reduced': fields.float(
            'Percentage of reduction for depreciation',
            digits_compute=dp.get_precision('Account')),
        'reduction_first_year': fields.float(
            'Percentage of reduction in first year',
            digits_compute=dp.get_precision('Account')),
        'early_ammortization': fields.float(
            'Percentage increase for depreciation',
            digits_compute=dp.get_precision('Account')),
        'maintenance_from_amortize': fields.float(
            'Percentage of Maintenance and Repair',
            digits_compute=dp.get_precision('Account')),
        'nmax_advanced_amortize': fields.integer(
            'Maximum number of anticipated depreciation'),
        'maintenance_account_id': fields.many2one(
            'account.account', 'Account Maintenance and Repair'),
        'gains_account_id': fields.many2one(
            'account.account', 'Account Gains'),
        'losses_account_id': fields.many2one(
            'account.account', 'Account Losses'),
        'deductibility': fields.float(
            'Percentage of deductibility',
            digits_compute=dp.get_precision('Account')),
        }


class account_asset_asset(orm.Model):

    _inherit = 'account.asset.asset'

    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        res = {}
        for asset in self.browse(cr, uid, ids, context):
            res[asset.id] = (asset.purchase_value - asset.salvage_value +
                             asset.incremental_value - asset.decremental_value)
        for id in ids:
            res.setdefault(id, 0.0)
        return res

    def _calc_variation(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for asset in self.browse(cr, uid, ids, context=context):
            result[asset.id] = {
                'incremental_value': 0.0,
                'decremental_value': 0.0,
                }
            for invoice in asset.invoice_line_ids:
                if invoice.new_asset:
                    continue
                if invoice.type == 'out_invoice' \
                        or invoice.type == 'in_refund':
                    if not invoice.total_sale:
                        result[asset.id][
                            'decremental_value'] += invoice.price_subtotal
                else:
                    result[asset.id][
                        'incremental_value'] += invoice.price_subtotal
        return result

    def _amount_accumulated(self, cr, uid, ids, fields, arg, context=None):
        result = {}
        for asset in self.browse(cr, uid, ids, context=context):
            result[asset.id] = {
                'accumulated_depreciation': 0.0,
                'remaining_value': 0.0,
                }
            for line in asset.depreciation_line_ids:
                result[asset.id]['accumulated_depreciation'] += line.amount
            result[asset.id]['remaining_value'] = (
                asset.value_residual - result[asset.id][
                    'accumulated_depreciation'])
        return result

    _columns = {
        'invoice_purchase_number':
            fields.char('Purchase Invoice number', size=25),
        'first_use_year': fields.many2one(
            'account.fiscalyear', 'Activivation Date'),
        'last_use_year': fields.many2one(
            'account.fiscalyear', 'Last Year of Use'),
        'deact_use_year': fields.many2one(
            'account.fiscalyear', 'Deactivation Date'),
        'next_use_year': fields.many2one(
            'account.fiscalyear', 'Next Use Year'),
        'type_amortization': fields.selection(
            (('O', 'ordinary'), ('F', 'first year reduction'),
             ('A', 'advance'), ('R', 'reduced'), ('P', 'personal')),
            'Amortization type'),
        'invoice_sale_number': fields.char('Sale Invoice number', size=25),
        'sale_date': fields.date(
            'Sale Date', help="Date of deactivation"),
        'sale_value': fields.float('Sale Value'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'deductibility': fields.float(
            'Percentage of deductibility',
            digits_compute=dp.get_precision('Account')),
        'incremental_value': fields.function(
            _calc_variation, type='float',
            string='Incremental Value', multi="variation"),
        'decremental_value': fields.function(
            _calc_variation, type='float',
            string='Decremental Value', multi="variation"),
        'value_residual': fields.function(
            _amount_residual, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Residual Value'),
        'accumulated_depreciation': fields.function(
            _amount_accumulated, method=True,
            digits_compute=dp.get_precision('Account'),
            string='Accumulated Depreciation',
            type='float', multi="amounts"),
        'gains': fields.float(
            'Gains', digits_compute=dp.get_precision('Account')),
        'losses': fields.float(
            'Losses', digits_compute=dp.get_precision('Account')),
        'remaining_value': fields.function(
            _amount_accumulated, method=True,
            digits_compute=dp.get_precision('Account'),
            string='accumulated depreciation', type='float', multi="amounts"),
        'ordinary_amortization': fields.float(
            'Ordinary Amortization',
            digits_compute=dp.get_precision('Account')),
        'amortization_reduced': fields.float(
            'Reduced Ammortization',
            digits_compute=dp.get_precision('Account')),
        'early_ammortization': fields.float(
            'Early Ammortization',
            digits_compute=dp.get_precision('Account')),
        'personal_ammortization': fields.float(
            'Personal Ammortization',
            digits_compute=dp.get_precision('Account')),
        'minor_use': fields.boolean('Minor Use'),
        'maintenance_accrued': fields.boolean('Maintenance in Accruals'),
        'used_asset': fields.boolean('Used'),
        'date_deactivate_maintenance': fields.date(
            'Deactivation Date Calculation Threshold Maintenance'),
        'depreciation_line_ids': fields.one2many(
            'account.asset.depreciation.line',
            'asset_id', 'Depreciation Lines'),
        'invoice_line_ids': fields.one2many(
            'account.invoice.line', 'asset_id',
            'Invoice Lines', readonly=True),
        }

    _defaults = {
        'deductibility': 100,
        'code': '/',
        }

    def create(self, cr, uid, vals, context=None):
        if vals.get('code', '/') == '/':
            vals['code'] = self.pool['ir.sequence'].get(
                cr, uid, 'account.asset.asset') or '/'
        asset_id = super(account_asset_asset, self).create(
            cr, uid, vals, context)
        return asset_id

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        # Sovrascritta perchè inutile
        pass
        return True
        
    def _compute_entries(self, cr, uid, ids, period_id, context=None):
        result = []
        period_obj = self.pool.get('account.period')
        depreciation_obj = self.pool.get('account.asset.depreciation.line')
        period = period_obj.browse(cr, uid, period_id, context=context)
        depreciation_ids = depreciation_obj.search(cr, uid, [
            ('asset_id', 'in', ids),
            ('depreciation_date', '<=', period.fiscalyear_id.date_stop), 
            ('depreciation_date', '>=', period.fiscalyear_id.date_start), 
            ], context=context)
        if depreciation_ids:
            list_pointer=0
            for line in depreciation_obj.browse(cr,uid,depreciation_ids):
                if line.move_check:
                    if context['at_day']:
                        raise osv.except_osv(
                            _('Errore'),
                            _('Previous moves amortization  found \
please delete those before' ))
                    else:
                        del depreciation_ids[list_pointer]
                list_pointer+=1            
        if context is None:
            context = {}
        context.update({'depreciation_date':period.date_stop})
        return depreciation_obj.create_move(cr, uid, depreciation_ids, context=context)

    
    def open_entries(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'search_default_asset_id': ids, 'default_asset_id': ids})
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }

    def name_get(self, cr, user, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        if not len(ids):
            return []

        def _name_get(d):
            name = d.get('name', '')
            code = d.get('code', False)
            if code:
                name = '[%s] %s' % (code, name)
            return (d['id'], name)
        result = []
        for asset in self.browse(cr, user, ids, context=context):
            mydict = {
                'id': asset.id,
                'name': asset.name,
                'code': asset.code,
                }
            result.append(_name_get(mydict))
        return result

    def calc_ammort(self, cr, uid, ids,
                    flag_overw, fiscal_year, tipo_calcolo, date, context={}):
        if not context:
            context = {}
        year_before_id, year_after_id = self.calc_period_prec(cr,
                                                              uid,
                                                              fiscal_year)
        line_asset = self.pool['account.asset.depreciation.line']
        asset_obj = self.pool['account.asset.asset']
        for asset in self.browse(cr, uid, ids):
            type_amortization = None
            if asset.type_amortization:
                type_amortization = 'O' if asset.type_amortization == 'F' else asset.type_amortization
            # verify that non exist amortization for the year
            if not asset.sale_date and asset.remaining_value > 0:
                line = {}
                sids = line_asset.search(
                    cr, uid,
                    [('fiscal_year', '=', fiscal_year.id),
                     ('asset_id', '=', asset.id)])
                if sids:
                    asset_line_year = line_asset.browse(cr, uid, sids[0])
                else:
                    asset_line_year = False

                # cerca l anno precedente per avere i dati di partenza.
                # per il caricamento di esercizi precedenti
                # ad odoo l'informazione
                # deve essere aggiornata alla save/create
                # della linea di ammortamento
                sids = line_asset.search(
                    cr, uid,
                    [('fiscal_year', '=', year_before_id),
                     ('asset_id', '=', asset.id)])
                if sids:
                    before_year_line = line_asset.browse(cr, uid, sids[0])
                else:
                    # non ho trovato l' ammortamento per il periodo precedente
                    # prima di dare errore deve verificare se è il primo anno
                    # o se non sta ricalcolando il periodo
                    # corrente che corrisponde
                    # al primo anno
                    # negli altri casi deve sempre esistere il periodo
                    # precedente a quello che si vuole calcolare.
                    if not (asset.first_use_year
                            and fiscal_year.id == asset.first_use_year.id):
                        raise osv.except_osv(
                            _('Errore'),
                            _('Previous amortization not found' + asset.name))
                    else:
                        # é il primo esercizio
                        before_year_line = False
                # è obbligatorio che sia inserito l' anno di primo esercizio
                if not asset.first_use_year:
                    raise osv.except_osv(
                        _('Error!'),
                        _('Set the fiscalyear for asset %s' % (asset.name)))
                if fiscal_year.id == asset.first_use_year.id:
                    # deve calcolare il primo anno
                    remaining_value = (
                        asset.value_residual -
                        (asset.ordinary_amortization *
                         asset.category_id.reduction_first_year / 100) *
                        asset.value_residual/100)
                    amount = (asset.ordinary_amortization *
                         asset.category_id.reduction_first_year /
                         100) * asset.value_residual/100
                    perc_ammortization = (
                        asset.ordinary_amortization *
                        asset.category_id.reduction_first_year / 100)
                    line = {
                        'asset_id': asset.id,
                        'name': fiscal_year.code,
                        'sequence': 1,
                        'fiscal_year': fiscal_year.id,
                        'depreciation_date': date,
                        'type_amortization': 'F',
                        'perc_ammortization': perc_ammortization,
                        'depreciated_value': 0.0,
                        'amount': amount,
                        'remaining_value': remaining_value
                        }
                    line_asset.create(cr, uid, line)
                    if not asset.first_use_year:
                        asset_obj.write(
                            cr, uid, [asset.id],
                            {'next_use_year': year_after_id,
                             'last_use_year': fiscal_year.id,
                             'first_use_year': fiscal_year.id,
                             'type_amortization': type_amortization}, context)
                    else:
                        asset_obj.write(
                            cr, uid, [asset.id],
                            {'next_use_year': year_after_id,
                             'last_use_year': fiscal_year.id,
                             'type_amortization': type_amortization}, context)
                else:
                    # si tratta di un anno diverso dal primo
                    # se sto calcolando l' anno nuovo posso prendere i dati
                    # del tipo di ammortamento dal cespite
                    # ma se devo ricalcolare un anno diverso
                    # non lo faccio e chiedo all' utente
                    # di cancellare le righe di ammortamento del cespite
                    if before_year_line:
                        if asset.next_use_year.id != fiscal_year.id:
                            raise osv.except_osv(
                                _('Error!'),
                                _('Reload for fiscal year %s \
and asset %s is not possible' % (asset.last_use_year.name, asset.name)))

                        if asset.type_amortization == 'O':
                            perc = asset.ordinary_amortization
                        if asset.type_amortization == 'R':
                            perc = asset.amortization_reduced
                        if asset.type_amortization == 'A':
                            anticipato_ids = line_asset.search(
                                cr, uid,
                                [('type_amortization', '=', 'A'),
                                 ('asset_id', '=', asset.id)])
                            nmax = asset.category_id.nmax_advanced_amortize
                            if anticipato_ids \
                                    and len(anticipato_ids) >= nmax:
                                raise osv.except_osv(
                                    _('Error!'),
                                    _('Exceeded the number of \
maximum number of anticipated depreciation for asset %s' % (asset.name)))
                            perc = asset.early_ammortization
                        if asset.type_amortization == 'P':
                            perc = asset.personal_ammortization
                        seq = len(asset.depreciation_line_ids) + 1
                        depreciated_value = asset.accumulated_depreciation
                        line = {
                            'asset_id': asset.id,
                            'sequence': seq,
                            'name': fiscal_year.code,
                            'fiscal_year': fiscal_year.id,
                            'depreciation_date': date,
                            'type_amortization': asset.type_amortization,
                            'perc_ammortization': perc,
                            'depreciated_value': depreciated_value,
                            }
                        line['amount'] = perc * asset.value_residual / 100
                        if line['amount'] >= asset.remaining_value:
                            line['amount'] = asset.remaining_value
                            line['remaining_value'] = 0.0
                        else:
                            line['remaining_value'] = (
                                asset.value_residual-line['amount'])
                    if line:
                        if asset_line_year:
                            # esiste già il verifico
                            # se deve riscrivere o meno
                            if flag_overw:
                                line_asset.write(
                                    cr, uid, [asset_line_year.id], line)
                                asset_obj.write(
                                    cr, uid, [asset.id],
                                    {'next_use_year': year_after_id,
                                     'last_use_year': fiscal_year.id,
                                     'type_amortization': type_amortization},
                                    context)
                        else:
                            line_asset.create(cr, uid, line, context)
                            asset_obj.write(
                                cr, uid, [asset.id],
                                {'next_use_year': year_after_id,
                                 'last_use_year': fiscal_year.id,
                                 'type_amortization': type_amortization}, context)
                    else:
                        raise osv.except_osv(
                            _('Error!'),
                            _('Not find the previous exercise for %s' % (
                              asset.name)))
        return True

    def calc_period_prec(self, cr, uid, fiscal_year, context={}):
        fiscalyear_obj = self.pool['account.fiscalyear']
        date_start = (
            str(datetime.strptime(fiscal_year.date_start, '%Y-%m-%d') -
                relativedelta(years=1))[:10])
        date_stop = (
            str(datetime.strptime(fiscal_year.date_stop, '%Y-%m-%d') -
                relativedelta(years=1))[:10])
        id_fy = fiscalyear_obj.search(
            cr, uid,
            [('date_start', '=', date_start), ('date_stop', '=', date_stop)])
        if not id_fy:
            raise osv.except_osv(
                _('Error!'),
                _('Not find the previous exercise for period %s - %s' % (
                  date_start, date_stop)))
        # Anno Successivo
        date_start = (
            str(datetime.strptime(fiscal_year.date_start, '%Y-%m-%d') +
                relativedelta(years=1))[:10])
        date_stop = (
            str(datetime.strptime(fiscal_year.date_stop, '%Y-%m-%d') +
                relativedelta(years=1))[:10])
        id_fy1 = fiscalyear_obj.search(
            cr, uid,
            [('date_start', '=', date_start), ('date_stop', '=', date_stop)])
        if not id_fy1:
            raise osv.except_osv(
                _('Error!'),
                _('Not find the next exercise for period %s - %s' % (
                  date_start, date_stop)))
        return id_fy[0], id_fy1[0]

    def onchange_category_id(self, cr, uid, ids, category_id, context={}):
        res = {'value': {}}
        asset_categ_obj = self.pool['account.asset.category']
        if not category_id:
            return res
        category_obj = asset_categ_obj.browse(
            cr, uid, category_id, context)
        ordinary_amortization = category_obj.ordinary_amortization
        amortization_reduced = (ordinary_amortization -
                                (ordinary_amortization *
                                 category_obj.amortization_reduced / 100))
        early_ammortization = (ordinary_amortization +
                               (ordinary_amortization *
                                category_obj.early_ammortization / 100))
        res['value'] = {
            'method': category_obj.method,
            'method_number': category_obj.method_number,
            'method_time': category_obj.method_time,
            'method_period': category_obj.method_period,
            'method_progress_factor': category_obj.method_progress_factor,
            'method_end': category_obj.method_end,
            'prorata': category_obj.prorata,
            'ordinary_amortization': ordinary_amortization,
            'amortization_reduced': amortization_reduced,
            'early_ammortization': early_ammortization,
            'deductibility': category_obj.deductibility,
            }
        return res

    def onchange_purchase_salvage_value(self, cr, uid, ids,
                                        purchase_value, salvage_value,
                                        incremental_value, decremental_value,
                                        deductibility, context={}):
        val = {}
        if purchase_value:
            val['salvage_value'] = purchase_value * (100 - deductibility) / 100
            val['value_residual'] = (purchase_value -
                                     val['salvage_value'] +
                                     incremental_value - decremental_value)
        if salvage_value:
            val['value_residual'] = (purchase_value - salvage_value +
                                     incremental_value - decremental_value)
        return {'value': val}

    def onchange_deductibility(self, cr, uid, ids, purchase_value,
                               deductibility, incremental_value,
                               decremental_value, context={}):
        val = {'deductibility': deductibility}
        if not deductibility:
            return val
        if (100 - deductibility) >= 0:
            if purchase_value:
                val['salvage_value'] = (purchase_value *
                                        (100 - deductibility) / 100)
                val['value_residual'] = (purchase_value -
                                         val['salvage_value'] +
                                         incremental_value - decremental_value)
        return {'value': val}


class account_asset_depreciation_line(orm.Model):

    _inherit = 'account.asset.depreciation.line'

    def _get_move_check(self, cr, uid, ids, name, args, context={}):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id)
        return res

    _columns = {
        'type_amortization': fields.selection(
            (('O', 'ordinary'), ('F', 'first year reduction'),
             ('A', 'advance'), ('R', 'reduced'), ('P', 'personal')),
            'Amortization type'),
        'perc_ammortization': fields.float(
            'Percentage amortization',
            digits_compute=dp.get_precision('Account')),
        'fiscal_year': fields.many2one(
            'account.fiscalyear', 'Fiscal Year'),
        'move_check': fields.function(
            _get_move_check, method=True, type='boolean', string='Posted', store=True),
        }

    def create_move(self, cr, uid, ids, context={}):
        move_obj = self.pool['account.move']
        move_line_obj = self.pool['account.move.line']
        if context.get('at_day',False):
            created_move_ids= self.create_move_parzial(cr, uid, ids, context)
        else:
            created_move_ids = super(
                account_asset_depreciation_line, self).create_move(
                    cr, uid, ids, context)
        if created_move_ids:
            for move in move_obj.browse(cr, uid, created_move_ids):
                if move.partner_id:
                    move_obj.write(
                        cr, uid, [move.id],
                        {'partner_id': False}, context)
                for line in move.line_id:
                    depreciation_date = context.get('depreciation_date') or line.depreciation_date or time.strftime('%Y-%m-%d')
                    move_obj.write(
                        cr, uid, [move.id],
                        {'document_date': depreciation_date}, context)
                    move_line_obj.write(
                        cr, uid, [line.id],
                        {'partner_id': False}, context)
        return created_move_ids

    def create_move_parzial(self, cr, uid, ids, context=None):
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
            ctx = dict(context, account_period_prefer_normal=True)
            period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})         
            if context.get('at_day',False):
                depreciation_date=context['to_day']
                
                fiscalyear = self.pool.get('account.fiscalyear').browse(cr,uid,context['fiscal_year'])
                ndays = (datetime.strptime(context['to_day'], "%Y-%m-%d")-datetime.strptime(fiscalyear.date_start, "%Y-%m-%d")).days
                val_amount = (line.amount/365)*ndays
            else:
                val_amount = line.amount
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, val_amount, context=context)
            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            asset_name = line.asset_id.name
            reference = line.name
            move_vals = {
                'date': depreciation_date,
                'ref': "%s %s" %(line.asset_id.code or line.asset_id.name, line.name),
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
            })
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.asset_id.category_id.account_analytic_id.id,
                'date': depreciation_date,
                'asset_id': line.asset_id.id
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.asset_id.id)
        return created_move_ids

class account_invoice_line(osv.osv):

    _inherit = 'account.invoice.line'
    _columns = {
        'asset_id': fields.many2one(
            'account.asset.asset', 'Asset', ondelete="restrict"),
        'new_asset': fields.boolean(
            'First Invoice', help="This line activated the asset"),
        'total_sale': fields.boolean(
            'Total Sale',
            help="This line deactivated the asset whit \
relavance of gains or losses"),
        'entry_ids': fields.one2many(
            'account.invoice.line', 'asset_id', 'Entries',
            readonly=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.related(
            'invoice_id', 'partner_id', type='many2one',
            relation='res.partner', string='Customer/Supplier'),
        'supplier_invoice_number': fields.related(
            'invoice_id', 'supplier_invoice_number', type='char',
            relation='account.invoice', string='Supplier Number'),
        'date_invoice': fields.related(
            'invoice_id', 'date_invoice', type='date',
            relation='account.invoice', string='Invoice Date'),
        'type': fields.related(
            'invoice_id', 'type', type='selection',
            relation='account.invoice',
            selection=[('out_invoice', 'Customer Invoice'),
                       ('in_invoice', 'Supplier Invoice'),
                       ('out_refund', 'Customer Refund'),
                       ('in_refund', 'Supplier Refund')], string='Type'),
        }

    def asset_create(self, cr, uid, lines, context={}):
        context = context or {}
        asset_obj = self.pool['account.asset.asset']
        for line in lines:
            if line.asset_id:
                # è indicato un cespite esistente se è un acquisto
                # tecnicamente non deve far nulla
                # verifica che non sia modifica della fattura
                # di acquisto iniziale per eventualmente
                # correggere gli importi
                # se è una fattura di vendita se c'è
                # il flag di chiusura cespite
                # deve far scattare le registrazioni
                # di minusvalenze e plusvalenze
                # segnare la fattura di vendita e chiudere il cespite
                invoice = line.invoice_id
                if line.new_asset:
                    # deve correggere gli importi del documento
                    invoice_purchase_num = invoice.supplier_invoice_number
                    fiscal_year = invoice.period_id.fiscalyear_id.id
                    vals = {
                        'purchase_value': line.price_subtotal,
                        'period_id': invoice.period_id.id,
                        'partner_id': invoice.partner_id.id,
                        'purchase_date': invoice.date_invoice,
                        'invoice_purchase_number': invoice_purchase_num,
                        'first_use_year': fiscal_year,
                        }
                    asset_obj.write(cr, uid, [line.asset_id.id], vals, context)
                if line.total_sale:
                    # vendita totale del bene e sua dismissione
                    vals = {
                        'sale_date': invoice.date_invoice,
                        'customer_id': invoice.partner_id.id,
                        'invoice_sale_number': invoice.number,
                        'sale_value': line.price_subtotal,
                        }
                    if (line.price_subtotal -
                            line.asset_id.remaining_value >= 0):
                        vals['gains'] = (line.price_subtotal -
                                         line.asset_id.remaining_value)
                    else:
                        vals['losses'] = ((line.price_subtotal -
                                          line.asset_id.remaining_value) * -1)
                    asset_obj.write(cr, uid, [line.asset_id.id], vals, context)
                    self.check_account_move(cr, uid, line, context)
                return True
            if line.asset_category_id:
                invoice = line.invoice_id
                vals = {
                    'name': line.name,
                    'code': '/',  # line.invoice_id.number or False,
                    'category_id': line.asset_category_id.id,
                    'purchase_value': line.price_subtotal,
                    'period_id': invoice.period_id.id,
                    'partner_id': invoice.partner_id.id,
                    'company_id': invoice.company_id.id,
                    'currency_id': invoice.currency_id.id,
                    'purchase_date': invoice.date_invoice,
                    'invoice_purchase_number': invoice.supplier_invoice_number,
                    'first_use_year': invoice.period_id.fiscalyear_id.id,
                    'type_amortization': 'O',
                    }
                changed_vals = asset_obj.onchange_category_id(
                    cr, uid, [], vals['category_id'], context)
                vals.update(changed_vals['value'])
                changed_vals = asset_obj.onchange_deductibility(
                    cr, uid, [], line.price_subtotal,
                    vals['deductibility'], 0.0, 0.0, context)
                vals.update(changed_vals['value'])
                asset_id = asset_obj.create(cr, uid, vals, context)
                self.write(
                    cr, uid, [line.id],
                    {'asset_id': asset_id, 'new_asset': True}, context)
                if line.asset_category_id.open_asset:
                    asset_obj.validate(cr, uid, [asset_id], context)
        return True

    def check_account_move(self, cr, uid, line, context={}):
        # Aggiunge le righe necessarie a chiudere il cespite in contabilita
        move_line_obj = self.pool['account.move.line']
        move = line.invoice_id.move_id
        asset = line.asset_id
        vals = {}
        valori = {}
        base = {
            'name': _("Asset sale %s" % (asset.name)),
            'ref': _("Asset sale %s" % (asset.name)),
            'move_id': move.id,
            'period_id': move.period_id.id,
            'journal_id': move.journal_id.id,
            'partner_id': False,
            'date': move.date,
            }
        vals.update(base)
        # Conto Asset
        amount = asset.value_residual - line.price_subtotal
        valori['account_id'] = asset.category_id.account_asset_id.id
        if amount > 0:
            valori['debit'] = 0.0
            valori['credit'] = amount
        else:
            amount = amount * -1
            valori['debit'] = amount
            valori['credit'] = 0.0
        if amount != 0:
            vals.update(valori)
            move_line_obj.create(cr, uid, vals, context)

        # Conto Fondo
        amount = asset.accumulated_depreciation
        valori['account_id'] = asset.category_id.account_depreciation_id.id
        if amount > 0:
            valori['debit'] = amount
            valori['credit'] = 0.0

        if amount != 0:
            vals.update(valori)
            move_line_obj.create(cr, uid, vals, context)
        # Conto Plusvalenza
        if asset.gains > 0:
            amount = asset.gains
            valori['account_id'] = asset.category_id.gains_account_id.id
            if amount > 0:
                valori['debit'] = 0.0
                valori['credit'] = amount

            if amount != 0:
                vals.update(valori)
                move_line_obj.create(cr, uid, vals, context)
        # Conto Minusvalenza
        if asset.losses > 0:
            amount = asset.losses
            valori['account_id'] = asset.category_id.losses_account_id.id
            if amount > 0:
                valori['debit'] = amount
                valori['credit'] = 0.0
            if amount != 0:
                vals.update(valori)
                move_line_obj.create(cr, uid, vals, context)
        return True

    def onchange_category_id(self, cr, uid, ids, category_id, context={}):
        res = {'value': {}}
        asset_categ_obj = self.pool['account.asset.category']
        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid,
                                                  category_id, context)
            res['value'] = {'account_id': category_obj.account_asset_id.id}
        return res

    def onchange_asset_id(self, cr, uid, ids, asset_id, context={}):
        res = {'value': {}}
        asset_obj = self.pool['account.asset.asset']
        if asset_id:
            asset_brw = asset_obj.browse(cr, uid, asset_id, context)
            res['value'] = {
                'account_id': asset_brw.category_id.account_asset_id.id}
        return res
