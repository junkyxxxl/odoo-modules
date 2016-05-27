# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import logging
from openerp.osv import osv

_logger = logging.getLogger('omniapart.partner.installer')


class omniapart_partner_installer(osv.osv_memory):
    _name = 'omniapart.partner.installer'
    _inherit = 'res.config.installer'

    _columns = {
    }

    def execute(self, cr, uid, ids, context=None):
        self.execute_simple(cr, uid, ids, context)
        return super(omniapart_partner_installer, self).execute(cr, uid, ids, context=context)

    def execute_simple(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        account_data = self.pool.get('account.account')
        partner_data = self.pool.get('res.partner')
        company_data = self.pool.get('res.company')
        '''
        cr.execute("SELECT cmp.id, acc1.id, acc2.id FROM account_account AS acc1, account_account AS acc2, res_company AS cmp WHERE acc1.company_id = cmp.id AND acc2.company_id = cmp.id AND acc1.code = '11201' AND acc2.code = '22505'")
        res = cr.fetchall()
        for row in res:
            company_data.write(cr, uid, row[0], {'subaccount_auto_generation_customer': True,
                                                 'subaccount_auto_generation_supplier': True,
                                                 'account_parent_customer': row[1],
                                                 'account_parent_supplier': row[2]})
        '''
        cr.execute("SELECT id,company_id,temporary_omniapart_receivable,temporary_omniapart_payable FROM res_partner")
        res = cr.fetchall()
        len_res = len(res)
        for i in range(0,len_res):
            row = res[i]
            _logger.info('Processando record: '+str(i)+'/'+str(len_res)) 
            if row[2]:
                cr.execute("SELECT id FROM account_account WHERE code = %s AND company_id = %s",(row[2],row[1]))
                account_id = cr.fetchall()
                if account_id and account_id[0]:
                    account_id = account_id[0][0]         
                account = account_data.browse(cr, uid, account_id)
                if account:
                    partner_data.write(cr, uid, row[0], {'property_account_receivable': account})
            if row[3]:
                cr.execute("SELECT id FROM account_account WHERE code = %s AND company_id = %s",(row[3],row[1]))
                account_id = cr.fetchall()
                if account_id and account_id[0]:
                    account_id = account_id[0][0]                              
                account = account_data.browse(cr, uid, account_id)
                if account:
                    partner_data.write(cr, uid, row[0], {'property_account_payable': account})