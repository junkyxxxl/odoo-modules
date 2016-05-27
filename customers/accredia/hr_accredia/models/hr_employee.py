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

from openerp.osv import orm


class hr_employee(orm.Model):
    _inherit = 'hr.employee'

    def onchange_user(self, cr, uid, ids, user_id, context=None):
        if context is None:
            context = {}
        res = super(hr_employee, self).onchange_user(cr, uid, ids, user_id, context=context)
        res['value']['department_id'] = None
        if user_id:
            user_obj = self.pool.get('res.users')
            user_data = user_obj.browse(cr, uid, user_id)
            if user_data.department_id:
                res['value']['department_id'] = user_data.department_id.id
        return res
