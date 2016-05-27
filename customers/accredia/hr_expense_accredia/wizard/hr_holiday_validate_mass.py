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

from openerp.osv import osv


class base_product_merge(osv.osv_memory):
    """
    Merges two products
    """
    _name = 'wizard.hr.holiday.validate'
    _description = 'Validate Holidays Massively'

    _columns = {
    }

    def do_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        t_active_ids = context.get('active_ids', [])

        if t_active_ids:
            t_holiday_obj = self.pool.get('hr.holidays')
            t_holiday_obj.holidays_validate(cr, uid, t_active_ids, context=context)

        return True
