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

from openerp.osv import fields, orm


class res_company_festivity(orm.Model):
    _name = 'res.company.festivity'
    _description = 'Day of festivity'

    _columns = {
        'name': fields.char('Name', size=80, required=True),
        'company_id': fields.many2one('res.company', 'Company Reference',
                                      required=True, ondelete="cascade",
                                      select=2),
        'year': fields.integer('Year'),
        'month': fields.integer('Month'),
        'day': fields.integer('Day'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: uid
    }

    _order = 'year desc'
    _order = 'month'
    _order = 'day'
