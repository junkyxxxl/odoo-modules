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
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class hr_employee_isa(orm.Model):
    _inherit = "hr.employee"
    _description = "Employee"

    def attendance_action_change(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        action_date = context.get('action_date', False)
        action = context.get('action', False)
        hr_attendance_obj = self.pool.get('hr.attendance')
        hr_action_reason_obj = self.pool.get('hr.action.reason')
        t_attendance = None
        warning_sign = {'sign_in': _('Sign In'), 'sign_out': _('Sign Out')}
        for employee in self.browse(cr, uid, ids, context=context):
            if not action:
                if employee.state == 'present': action = 'sign_out'
                if employee.state == 'absent': action = 'sign_in'

            if not super(hr_employee_isa, self)._action_check(cr, uid, employee.id, action_date, context):
                raise orm.except_orm(_('Warning'), _('You tried to %s with a date anterior to another event !\nTry to contact the HR Manager to correct attendances.')%(warning_sign[action],))

            vals = {'action': action, 'employee_id': employee.id}
            if action_date:
                vals['name'] = action_date
            attendance_ids = hr_attendance_obj.search(cr, uid, [('employee_id', '=', employee.id)],
                                                      order='create_date desc')
            t_date = fields.date.context_today(self, cr, uid, context=context)
            t_today = t_date[:10]
            if attendance_ids:
                t_attendance = hr_attendance_obj.browse(cr, uid, attendance_ids[0])
            if(t_attendance and t_attendance.name[:10] != t_today):
                t_reason_id = hr_action_reason_obj.search(cr, uid, [('name', '=', 'Entrata iniziale')])[0]
                vals['action_desc'] = t_reason_id
            elif(t_attendance and t_attendance.name[:10] == t_today):
                t_reason_name = t_attendance.action_desc.name
                if(t_reason_name == 'Uscita per fine giornata'):
                    raise orm.except_orm(_('Attenzione'), _("Hai già inserito l'uscita per fine giornata.\
                                                            Controlla le tue presenze odierne e \
                                                            ricorda di aggiornare la pagina (F5)"))
                if(t_reason_name == 'Uscita per servizio'):
                    t_reason_id = hr_action_reason_obj.search(cr, uid, [('name', '=', 'Rientro da servizio')])[0]
                    vals['action_desc'] = t_reason_id 
                if(t_reason_name == 'Uscita per permesso'):
                    t_reason_id = hr_action_reason_obj.search(cr, uid, [('name', '=', 'Rientro da permesso')])[0]
                    vals['action_desc'] = t_reason_id 
                if(t_reason_name == 'Uscita per pausa pranzo'):
                    t_reason_id = hr_action_reason_obj.search(cr, uid, [('name', '=', 'Rientro da pausa pranzo')])[0]
                    vals['action_desc'] = t_reason_id 
            hr_attendance_obj.create(cr, uid, vals, context=context)
        return True

    def attendance_action_exit(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        hr_attendance_obj = self.pool.get('hr.attendance')

        for employee in self.browse(cr, uid, ids, context=context):

            attendance_ids = hr_attendance_obj.search(cr, uid,
                                                      [('employee_id', '=', employee.id)],
                                                      limit=1,
                                                      order='create_date desc')
            if attendance_ids:
                return attendance_ids[0]
        return True
