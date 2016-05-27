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



from openerp.osv import osv

class mail_followers_omniapart(osv.Model):

    _inherit = 'mail.followers'

    def create(self, cr, uid, vals, context=None):
        if 'res_model' in vals and 'res_id' in vals and vals['res_model'] in ['project.project','project.task']:
            if 'subtype_ids' in vals:
                vals['subtype_ids'] = None
        return super(mail_followers_omniapart, self).create(cr, uid, vals, context=context)