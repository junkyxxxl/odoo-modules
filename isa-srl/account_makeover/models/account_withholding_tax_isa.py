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


class account_withholding_tax_isa(orm.Model):

    _name = "account.withholding.tax.isa"

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        return company_id

    def _get_default_wht_payment_term(self, cr, uid, context=None):
        if context is None:
            context = {}
        p_term_obj = self.pool.get('account.payment.term')
        p_term_search = p_term_obj.search(cr, uid,
                                          [('name', '=', '16th Next Month')],
                                          limit=1)
        res = None
        if not p_term_search:
            raise orm.except_orm(_('Error!'),
    			(_('Payment term "16th Next Month" missing!')))
        else:
            p_term_res = p_term_obj.browse(cr, uid, p_term_search,
                                           context=context)
            res = p_term_res and p_term_res[0].id
        return res

    def name_get(self, cr, uid, ids, context=None):
        if not len(ids):
            return []
        res = []
        for t_wht_name in self.browse(cr, uid, ids):
            descr = ("%s  %s") % (t_wht_name.name,
                                  t_wht_name.description)
            res.append((t_wht_name.id, descr))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                                                context=None, limit=100):
        if args is None:
            args = []
        if context is None:
            context = {}

        req_ids = self.search(cr, uid, args + 
                              ['|',
                               ('name', operator, name),
                               ('description', operator, name)],
                                limit=limit,
                                context=context)
        return self.name_get(cr, uid, req_ids, context=context)

    def onchange_company_id(self, cr, uid, ids, context=None):
        return {'value': {'wht_journal_id':None,'account_id':None},}

    _columns = {
        'name': fields.char('Code', size=5,
                            help="Codice fornito dall'Agenzia delle Entrate"),
        'description': fields.text('Description'),
        'wht_payment_term': fields.many2one('account.payment.term',
                                      'Payment Terms',
                                      help="It refers to the Payment Term for the Withholding Tax"),
        'wht_tax_rate': fields.float('Tax Rate'),
        'wht_base_amount':  fields.float('Tax/Base Amount'),
        'wht_journal_id': fields.many2one('account.journal',
                                      'Account Journal',
                                      domain="[('company_id','=',company_id)]",                                      
                                      help="It refers to the Journal to be used for the notice of the Withholding Tax",),
        'company_id': fields.many2one('res.company','Company',help="It refers to the company that will use the Witholding Tax"),        
        'account_id': fields.many2one('account.account',
                                      'Account',
                                      domain="[('type', '!=', 'view'),('company_id','=',company_id)]",
                                      help="It refers to the Account for the Withholding Taxes to be paid"),
        }

    _defaults = {
        'wht_payment_term': _get_default_wht_payment_term,
        'wht_tax_rate': 20.0,
        'wht_base_amount':  100.0,
        'company_id': _get_default_company,
        }
