# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging

from openerp import tools

from email.header import decode_header
from email.utils import formataddr
from openerp import SUPERUSER_ID, api
from openerp.osv import osv, orm, fields
from openerp.tools import html_email_clean
from openerp.tools.translate import _
from HTMLParser import HTMLParser

_logger = logging.getLogger('mail.message')

class mail_message_multicompany(osv.Model):

    _inherit = 'mail.message'

    def _get_company_id(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for item in self.browse(cr, uid, ids, context=context):
            result[item.id] = None
            if not item.model or not item.res_id:
                continue
            try:
                data = self.pool.get(item.model).browse(cr,uid,item.res_id)
                if 'company_id' in data._fields and data.company_id:
                    result[item.id] = data.company_id.id                
            except:
                _logger.info('Exception Message: '+str(item.id)+'referred to Model: '+item.model+' - ID: '+str(item.res_id)) 
        return result

    _columns = {
        'related_company_id': fields.function(_get_company_id, type='many2one', relation='res.company', store=True, string='Company')
    }

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]
        ctx['without_check'] = True
        return super(mail_message_multicompany,self).read(cr, uid, ids, fields, context=ctx, load=load)

    def check_access_rule(self, cr, uid, ids, operation, context=None):
        if not context:
            context = {}
        if 'without_check' in context and context['without_check']:
            return 
        return super(mail_message_multicompany,self).check_access_rule(cr, uid, ids, operation, context=context)