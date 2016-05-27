# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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


from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from math import ceil
import openerp.addons.decimal_precision as dp

class wizard_migration_province(osv.osv_memory):
    _name = "wizard.migration.province"
    _description = "Migrate Province"

    _columns = {}


    def migrate_province(self, cr, uid, ids, context=None):
        partner_obj = self.pool.get('res.partner')
        zip_obj = self.pool.get('res.better.zip')
        state_obj = self.pool.get('res.country.state')
        
        for partner_id in partner_obj.search(cr, uid, [('id','>',0)]):
            partner_data = partner_obj.browse(cr, uid, partner_id)
            if partner_data.country_id and partner_data.province:
                state_id = state_obj.search(cr, uid, [('code','=',partner_data.province.code),('country_id','=',partner_data.country_id.id)], context=context)
                if state_id:
                    partner_obj.write(cr, uid, partner_id, {'state_id': state_id[0]}, context=context)
                                
        return 


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

    