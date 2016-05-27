# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
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
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class ResPartner(orm.Model):
    _inherit = 'res.partner'
    
    def _default_subaccount_auto_generation_customer(self, cr, uid, context=None):
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        t_value = my_company.subaccount_auto_generation_customer
        return t_value
    
    def _default_subaccount_auto_generation_supplier(self, cr, uid, context=None):
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        t_value = my_company.subaccount_auto_generation_supplier
        return t_value
    
    _columns = {
        'wht_account_id': fields.many2one('account.withholding.tax.isa',
                                          'Withholding account',
                                          domain="[('company_id','=',company_id)]",
                                          help='Payable account used for amount due to tax authority'),
        'subaccount_auto_generation_customer': fields.related('company_id',
                                                              'subaccount_auto_generation_customer',
                                                              type='boolean',
                                                              string='Customers Subaccount Automatic Generation', readonly=1),
        'subaccount_auto_generation_supplier': fields.related('company_id',
                                                              'subaccount_auto_generation_supplier',
                                                              type='boolean',
                                                              string='Suppliers Subaccount Automatic Generation', readonly=1),
        }

    _defaults = {
                 'subaccount_auto_generation_customer': _default_subaccount_auto_generation_customer,
                 'subaccount_auto_generation_supplier': _default_subaccount_auto_generation_supplier,
                 }

    def onchange_customer_flag(self, cr, uid, ids, customer_flag, context=None):
        warning = {}
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        if(not my_company.subaccount_auto_generation_customer and customer_flag and ids):
            warning = {
                       'title': _('Warning!'),
                       'message': _('Remember to check the credit account in the Accounting Tab')
                       }
        return {'value': {},
                'warning': warning
                 }

    def onchange_supplier_flag(self, cr, uid, ids, supplier_flag, context=None):
        warning = {}
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        if(not my_company.subaccount_auto_generation_supplier and supplier_flag and ids):
            warning = {
                       'title': _('Warning!'),
                       'message': _('Remember to check the debit account in the Accounting Tab')
                       }
        return {'value': {},
                'warning': warning
                 }

    def _get_type_receivable_id(self, cr, uid):
        account_type_obj = self.pool.get('account.account.type')
        account_type_receivable_ids = account_type_obj.search(cr, uid,
                                                    [('code', '=', 'receivable')])
        if not account_type_receivable_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Nessun tipo conto: Credito definito'))
        return account_type_receivable_ids[0]

    def _get_type_payable_id(self, cr, uid):
        account_type_obj = self.pool.get('account.account.type')
        account_type_payable_ids = account_type_obj.search(cr, uid,
                                                    [('code', '=', 'payable')])
        if not account_type_payable_ids:
            raise orm.except_orm(_('Error!'),
                                 _('Nessun tipo conto: Debito definito'))
        return account_type_payable_ids[0]

    def _get_subaccounts(self, cr, uid, ids, vals, t_customer_flag, account_receivable_ids, t_partner_name, t_supplier_flag, account_payable_ids):

        account_receivable_id = None
        account_payable_id = None

        account_obj = self.pool.get('account.account')
        res_partner_obj = self.pool.get('res.partner')
        partner_data = res_partner_obj.browse(cr,uid,ids)
        if partner_data and len(partner_data) == 1:
            my_company = partner_data.company_id
        else:
            res_users_obj = self.pool.get('res.users')
            my_company = res_users_obj.browse(cr, uid, uid).company_id

        if (my_company.subaccount_auto_generation_customer and t_customer_flag and not account_receivable_ids):
            account_type_receivable_id = self._get_type_receivable_id(cr, uid)
            account_receivable_code = account_obj.get_max_code(cr, uid, my_company.account_parent_customer.id, my_company.account_parent_customer.id)
            account_receivable_dict = {'name': t_partner_name,
                                       'code': account_receivable_code,
                                       'parent_id': my_company.account_parent_customer.id,
                                       'type': 'receivable',
                                       'user_type': account_type_receivable_id,
                                       'company_id': my_company.id,
                                       'reconcile': True}
            account_receivable_id = account_obj.create(cr, uid, account_receivable_dict)
            vals["property_account_receivable"] = account_receivable_id

        if (my_company.subaccount_auto_generation_supplier and t_supplier_flag and not account_payable_ids):
            account_type_payable_id = self._get_type_payable_id(cr, uid)
            account_payable_code = account_obj.get_max_code(cr, uid, my_company.account_parent_supplier.id, my_company.account_parent_supplier.id)
            account_payable_dict = {'name': t_partner_name,
                                    'code': account_payable_code,
                                    'parent_id': my_company.account_parent_supplier.id,
                                    'type': 'payable',
                                    'user_type': account_type_payable_id,
                                    'company_id': my_company.id,
                                    'reconcile': True}
            account_payable_id = account_obj.create(cr, uid, account_payable_dict)
            vals["property_account_payable"] = account_payable_id

        return vals, account_receivable_id, account_payable_id

    def _check_account(self, cr, uid, ids, context=None):
        prop_obj = self.pool.get('ir.property')
        for id in ids:
            customer = self.browse(cr,uid,id,context=context).customer
            supplier = self.browse(cr,uid,id,context=context).supplier
            property_account_receivable = str(self.browse(cr,uid,id,context=context).property_account_receivable.id)            
            property_account_payable = str(self.browse(cr,uid,id,context=context).property_account_payable.id)
            if self.browse(cr,uid,id,context=context).is_company:
                if customer:
                    tmp = prop_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','in',[False,None,''])])
                    tmp_id = []
                    for item in tmp:
                        t_str = prop_obj.browse(cr,uid,item,context=context).value_reference
                        tmp_id.append(t_str.partition(',')[2])
                    if property_account_receivable in tmp_id:
                        return False
        
                if supplier:
                    tmp = prop_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','in',[False,None,''])])
                    tmp_id = []
                    for item in tmp:
                        t_str = prop_obj.browse(cr,uid,item,context=context).value_reference
                        tmp_id.append(t_str.partition(',')[2])            
                    if property_account_payable in tmp_id:
                        return False
            
        return True
    
    '''
    _constraints = [
        (_check_account, 'Bisogna impostare conti personalizzati per il partner', 
         ['customer','supplier','property_account_receivable','property_account_payable','is_company']),
    ]
    '''

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        account_receivable_ids = []
        account_payable_ids = []

        t_partner_name = None
        t_customer_flag = None
        t_supplier_flag = None
        if ('name' in vals):
            t_partner_name = vals["name"]
        if ('customer' in vals):
            t_customer_flag = vals["customer"]
        if ('supplier' in vals):
            t_supplier_flag = vals["supplier"]

        vals, account_receivable_id, account_payable_id = self._get_subaccounts(
                                     cr, uid, [], vals, t_customer_flag,
                                     account_receivable_ids, t_partner_name,
                                     t_supplier_flag, account_payable_ids)
        res_id = super(ResPartner, self).create(cr, uid, vals, context)
        account_obj = self.pool.get('account.account')
        if(account_receivable_id):
            account_obj.write(cr, uid, [account_receivable_id], {'partner_id':res_id})
        if(account_payable_id):
            account_obj.write(cr, uid, [account_payable_id], {'partner_id':res_id})
        return res_id

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        account_receivable_ids = []
        account_payable_ids = []
        t_partner_name = None
        t_customer_flag = None
        t_supplier_flag = None
        if ids:
            t_partner = self.browse(cr, uid, ids[0])
            account_obj = self.pool.get('account.account')
            account_receivable_ids = account_obj.search(cr, uid,
                                                [('partner_id', '=', ids[0]),
                                                 ('user_type.code', '=', 'receivable')])
            account_payable_ids = account_obj.search(cr, uid,
                                                     [('partner_id', '=', ids[0]), 
                    ('user_type.code', '=', 'payable')])
            t_partner_name = t_partner.name
            t_customer_flag = t_partner.customer
            t_supplier_flag = t_partner.supplier

        if 'name' in vals:
            t_partner_name = vals["name"]
        if 'customer' in vals:
            t_customer_flag = vals["customer"]
        if 'supplier' in vals:
            t_supplier_flag = vals["supplier"]

        vals, account_receivable_id, account_payable_id = self._get_subaccounts(
                                     cr, uid, ids, vals, t_customer_flag,
                                     account_receivable_ids, t_partner_name,
                                     t_supplier_flag, account_payable_ids)
        t_write = super(ResPartner, self).write(cr, uid, ids, vals, context)
        if ids:
            res_id = ids[0]
            account_obj = self.pool.get('account.account')
            if(account_receivable_id):
                account_obj.write(cr, uid, [account_receivable_id], {'partner_id':res_id})
            if(account_payable_id):
                account_obj.write(cr, uid, [account_payable_id], {'partner_id':res_id})
        return t_write

    def onchange_vat(self, cr, uid, ids, value, position, context=None):
        warning = {}
        if value and position != 2:
            t_partner_ids = self.search(cr, uid, [('vat', '=', value)])
            if t_partner_ids:
                warning = {
                           'title': _('Warning!'),
                           'message': _('There is another partner with the same VAT code.')
                           }
        return {'value': {'vat_subjected': bool(value)},
                'warning': warning
                 }
