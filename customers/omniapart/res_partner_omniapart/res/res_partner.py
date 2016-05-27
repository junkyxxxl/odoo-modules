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

from openerp.osv import fields, osv


class res_partner(osv.osv):

    _inherit = "res.partner"

    _columns = {
        'is_group': fields.boolean('Part of a Group', help="Check this box if this company is joined to a group."),
        'is_partner_level2': fields.boolean('Prospect'),
        'omnia_parent_name': fields.char('Group Name'),

        'average_sales_volume': fields.float(string='Average sales volume'),
        'subcontractors_number': fields.integer('N. Subcontractors'),
        'det_period_employees': fields.integer('Determined'),
        'undet_period_employees': fields.integer('Undetermined'),
        'part_time_employees': fields.integer('Part-time'),
        'total_employees': fields.integer('Total'),

        'temporary_omniapart_receivable': fields.char('Temporary Omniapart Receivable', size=64),
        'temporary_omniapart_payable': fields.char('Temporary Omniapart Payable', size=64),

        'date_certification': fields.date('Required Certification Date'),
    }

    _defaults = {
        'is_partner_level2': False,
    }

    def on_change_is_partner_level2(self, cr, uid, ids, is_partner_level2, context=None):    
        if is_partner_level2:
            return {'value': {'supplier': False, 'customer': False,}}
        return {}