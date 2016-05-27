# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Giuseppe D'Alò (<g.dalo@apuliasoftware.it>)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.exceptions import except_orm, Warning


class account_fiscal_position(orm.Model):

    _inherit = "account.fiscal.position"
    _columns = {
        'xcash_vat': fields.boolean('Active per cash vat'),
        'check_enforceability_vat': fields.boolean(
            'Check date enforceability vat '),
        }


class account_journal(orm.Model):

    _inherit = "account.journal"

    _columns = {
        'xcash_vat': fields.boolean('Active per cash vat'),
        }


class account_tax_code(orm.Model):

    _inherit = "account.tax.code"

    _columns = {
        'xcash_vat': fields.boolean('Active per cash vat'),
        'xcash_tax_code': fields.many2one('account.tax.code',
                                          'Reverse Tax Code'),
        }


class account_tax(orm.Model):

    _inherit = "account.tax"

    _columns = {
        'xcash_vat': fields.boolean('Active per cash vat'),
        }


class res_company(orm.Model):

    _inherit = "res.company"

    _columns = {
        'date_start_xcash': fields.date('Date Start', required=False),
        'date_stop_xcash': fields.date('Date Stop', required=False),
        'xcash_vat': fields.boolean('Active per cash vat'),
        'fiscal_position_id': fields.many2one(
            'account.fiscal.position', 'Fiscal Position per Cash'),
        'journal_purch_xcash_id': fields.many2one(
            'account.journal', 'Journal Purchase invoice per Cash vat'),
        'journal_sale_xcash_id': fields.many2one(
            'account.journal', 'Journal Sale invoice per Cash vat'),
        'journal_purch_xcash_matured_id': fields.many2one(
            'account.journal', 'Journal Purchase invoice per Cash vat matured'),
        'journal_sale_xcash_matured_id': fields.many2one(
            'account.journal', 'Journal Sale invoice per Cash vat matured'),
        'accounts_xcashids': fields.one2many(
            'xcash.link.account', 'company_id', 'Accounts',
            help='Link of link between normal and xcash vat account',),
        }

    def start_xcash(self, cr, uid, ids, context=None):
        for company in self.browse(cr, uid, ids):
            if not company.fiscal_position_id:
                raise except_orm(
                    _('Invalid Action!'),
                    _('Define a Fiscal Position before'))
            if not company.accounts_xcashids:
                raise except_orm(
                    _('Invalid Action!'),
                    _('Define links of accounts before'))
        self.check_tax_taxcode(cr, uid, ids, company)
        self.write(cr, uid, ids,
                   {'xcash_vat': True,
                    'date_start_xcash': fields.datetime.now()})
        return True

    def stop_xcash(self, cr, uid, ids, context=None):
        data_reg = fields.datetime.now()
        self.write(cr, uid, ids,
                   {'xcash_vat': False,
                    'date_stop_xcash': data_reg})
        self.check_matured_invoice(cr, uid, ids, data_reg)
        
        return True

    def check_matured_invoice(self, cr, uid, ids, data_reg,context={}):
        invoice_obj = self.pool['account.invoice']
        period_obj = self.pool['account.period']
        liq_obj = self.pool['account.vat.period.end.statement']
        company = self.pool['res.users'].browse(cr, uid, uid).company_id
        #period_ids = self.browse(cr, uid, ids[0]).period_ids
        #~ old_periods = []
        #~ import pdb; pdb.set_trace()
        #~ for period in self.browse(cr, uid, ids[0]).period_ids:
            #~ data_sca = datetime.strptime(period.date_start, '%Y-%m-%d')
            #~ date_test = data_sca + relativedelta(years=-1)            
            #~ periodo = period_obj.find(cr, uid, date_test)
            #~ if periodo:
                #~ old_periods.append(periodo[0])
        # ha definito il range  della liquidazione
        # ora cerchiamo le fatture di un anno indietro
        if company:
            # prepara la query per trovare tutte le fatture che rientrano
            #nel periodo
            cerca = []
            #~ cerca.append(('period_id', 'in', old_periods))
            cerca.append(('company_id', '=', company.id))
            cerca.append(('journal_id', 'in',
            [company.journal_purch_xcash_id.id,
                company.journal_sale_xcash_id.id]))
            cerca.append(('amount_tax_remain', '>', 0.1))
            cerca.append(('registration_date', '<=', data_reg ))
            cerca.append(('state', 'in', ['open','paid']))
            invoice_ids = invoice_obj.search(cr, uid, cerca)
            if invoice_ids:
                #ci sono fatture che andrebbero stornate
                liq_obj.action_move_line_x_cash(cr, uid, ids, invoice_ids, data_reg)
        return True

    def check_tax_taxcode(self, cr, uid, ids, company, context=None):
        # Se non trova tasse e conti tassa con il flag xcash_vat attivo allora
        # duplica tutti i conti tassa e tassa attivandogli il flag
        tax_code_obj = self.pool['account.tax.code']
        xcash_link_obj = self.pool['xcash.link.account']
        tax_obj = self.pool['account.tax']
        tax_codes_ids = tax_code_obj.search(
            cr, uid, [('xcash_vat', '=', True),('company_id', '=', company.id)])
        if not tax_codes_ids:
            tax_codes_ids = tax_code_obj.search(cr, uid, [('company_id', '=', company.id)], order='code')
            for tax_code in tax_code_obj.browse(cr, uid, tax_codes_ids):
                if tax_code.code:
                    tax_dic = {
                        'xcash_vat': True,
                        'name': tax_code.name + ' x cassa',
                        'code': tax_code.code + 'xc',
                        }
                if tax_code.vat_statement_account_id:
                    account_id = tax_code.vat_statement_account_id.id
                    account_xcash_ids = xcash_link_obj.search(
                        cr, uid,
                        [('company_id', '=', ids[0]),
                         ('account_id', '=', account_id)])
                    if account_xcash_ids:
                        account_xcash = xcash_link_obj.browse(
                            cr, uid, account_xcash_ids[0])
                        tax_dic[
                            'vat_statement_account_id'
                            ] = account_xcash.account_xcash_id.id
                    else:
                        raise except_orm(
                            _('Invalid Action1!'),
                            _('Reference for account %s not found, \n azienda conto %s \n conto tassa %s' ) %
                             (tax_code.vat_statement_account_id.code,tax_code.vat_statement_account_id.company_id.name, tax_code.code))
                new_tax_code = tax_code_obj.copy(cr, uid, tax_code.id, tax_dic)
                tax_code_obj.write(
                    cr, uid, [tax_code.id], {'xcash_tax_code': new_tax_code},
                    context)
                tax_code_obj.write(
                    cr, uid, [new_tax_code], {'xcash_tax_code': tax_code.id},
                    context)

            tax_codes_ids = tax_code_obj.search(cr, uid,
                                                [('xcash_vat', '=', True),('company_id', '=', company.id)])
            for tax_code in tax_code_obj.browse(cr, uid, tax_codes_ids):
                if tax_code.parent_id:
                    if tax_code.parent_id.code:
                        parent_id = tax_code_obj.search(
                            cr, uid,
                            [('code', '=', tax_code.parent_id.code + 'xc'),('company_id', '=', company.id)])
                        if parent_id:
                            tax_code_obj.write(
                                cr, uid, [tax_code.id],
                                {'parent_id': parent_id[0]})
                        else:
                            raise except_orm(
                                _('Invalid Action!'),
                                _('Parent tax code of %s not found ') %
                                 (tax_code.code))
        tax_ids = tax_obj.search(cr, uid, [('xcash_vat', '=', True),('company_id', '=', company.id)])
        #~ import pdb; pdb.set_trace()
        if not tax_ids:
            tax_ids = tax_obj.search(cr, uid, [('company_id', '=', company.id)])
            for tax in tax_obj.browse(cr, uid, tax_ids):
                tax_dic = {
                    'xcash_vat': True,
                    'name': tax.name + ' x cassa',
                    'description': tax.description + 'xc'}
                if tax.account_collected_id:
                    account_xcash_ids = xcash_link_obj.search(
                        cr, uid,
                        [('company_id', '=', ids[0]),
                         ('account_id', '=', tax.account_collected_id.id)])
                    if account_xcash_ids:
                        account_xcash = xcash_link_obj.browse(
                            cr, uid, account_xcash_ids[0])
                        tax_dic[
                            'account_collected_id'
                            ] = account_xcash.account_xcash_id.id
                    else:
                        raise except_orm(
                            _('Invalid Action2!'),
                            _('Reference for account %s not found , \n azienda conto %s \n  tassa %s \n azienda tassa %s \n id tassa %s') %
                             (tax.account_collected_id.code, tax.account_collected_id.company_id.name,tax.description,tax.company_id.name, tax.id))
                if tax.account_paid_id:
                    account_xcash_ids = xcash_link_obj.search(
                        cr, uid,
                        [('company_id', '=', ids[0]),
                         ('account_id', '=', tax.account_paid_id.id)])
                    if account_xcash_ids:
                        account_xcash = xcash_link_obj.browse(
                            cr, uid, account_xcash_ids[0])
                        tax_dic[
                            'account_paid_id'
                            ] = account_xcash.account_xcash_id.id
                    else:
                        raise except_orm(
                            _('Invalid Action3!'),
                            _('Reference for account %s not found  \n azienda conto %s \n  tassa %s') %
                             (tax.account_paid_id.code,tax.account_paid_id,company_id.name, tax.description))
                if tax.base_code_id:
                    tax_code_id = tax_code_obj.search(
                        cr, uid,
                        [('code', '=', tax.base_code_id.code + 'xc'),('company_id', '=', company.id)])
                    if tax_code_id:
                        tax_dic['base_code_id'] = tax_code_id[0]
                    else:
                        raise except_orm(
                            _('Invalid Action!'),
                            _('Reference for tax code %s not found') %
                             (tax.base_code_id.code))
                if tax.ref_base_code_id:
                    tax_code_id = tax_code_obj.search(
                        cr, uid,
                        [('code', '=', tax.ref_base_code_id.code + 'xc'),('company_id', '=', company.id)])
                    if tax_code_id:
                        tax_dic['ref_base_code_id'] = tax_code_id[0]
                    else:
                        raise except_orm(
                            _('Invalid Action!'),
                            _('Reference for tax code %s not found') %
                             (tax.ref_base_code_id.code))
                if tax.tax_code_id:
                    tax_code_id = tax_code_obj.search(
                        cr, uid, [('code', '=', tax.tax_code_id.code + 'xc'),('company_id', '=', company.id)])
                    if tax_code_id:
                        tax_dic['tax_code_id'] = tax_code_id[0]
                    else:
                        raise except_orm(
                            _('Invalid Action!'),
                            _('Reference for tax code %s not found') %
                             (tax.tax_code_id.code))
                if tax.ref_tax_code_id:
                    tax_code_id = tax_code_obj.search(
                        cr, uid,
                        [('code', '=', tax.ref_tax_code_id.code + 'xc'),('company_id', '=', company.id)])
                    if tax_code_id:
                        tax_dic['ref_tax_code_id'] = tax_code_id[0]
                    else:
                        raise except_orm(
                            _('Invalid Action!'),
                            _('Reference for tax code %s not found') %
                             (tax.ref_tax_code_id.code))
                new_tax = tax_obj.copy(cr, uid, tax.id, tax_dic)
                if new_tax:
                    self.pool.get('account.fiscal.position.tax').create(
                        cr, uid, {
                            'position_id': company.fiscal_position_id.id,
                            'tax_src_id': tax.id,
                            'tax_dest_id': new_tax})
                    tax_obj.write(
                        cr, uid, [new_tax],
                        {'name': tax.name + ' x cassa'})
        return True

    def check_enforceability_vat(self, cr, uid, ids, context=None):
        return True


class xcash_link_account(orm.Model):

    _name = "xcash.link.account"

    _description = "List of account xchash and normal link"

    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
        'account_xcash_id': fields.many2one(
            'account.account', 'Account per Cash vat', required=True),
        'account_id': fields.many2one(
            'account.account', 'Account normal vat', required=True),
        }

    def _get_related_account(self, cr, uid, account_id,
                             company_id=False, context={}):
        if not company_id:
            company_id = self.browse(cr, uid, uid).company_id.id
        res = self.search(cr, uid, [('account_xcash_id', '=', account_id),
                                    ('company_id', '=', company_id)])
        if not res:
            raise Warning(_('Relazione non definita'))
        return self.browse(cr, uid, res[0]).account_id.id
