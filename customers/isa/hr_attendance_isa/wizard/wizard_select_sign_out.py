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

class wizard_select_sign_out(orm.TransientModel):
    _name = 'wizard.select.sign.out'
    _description = 'Wizard Select Sign Out'

    _columns = {'reason_id': fields.many2one('hr.action.reason',
                                             'Reason'),
                'attendance_id': fields.many2one('hr.attendance',
                                                 'Presenza'),
                }

    def confirm(self, cr, uid, ids, context=None):
        attendance_obj = self.pool.get('hr.attendance')
        t_reason_id = None
        t_attendance_id = None
        form = self.read(cr, uid, ids)[0]
        if form["reason_id"]:
            t_reason_id = form["reason_id"][0]
        if form["attendance_id"]:
            t_attendance_id = form["attendance_id"][0]

        if t_reason_id and t_attendance_id:
            vals = {'action_desc': t_reason_id}
            attendance_obj.write(cr, uid, [t_attendance_id], vals, context)

        return True
