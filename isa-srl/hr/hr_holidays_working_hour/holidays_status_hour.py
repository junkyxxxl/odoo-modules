# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime
import datetime

class working_hour(models.Model):
    _inherit = 'hr.holidays.status'

    def get_days(self, cr, uid, ids, employee_id, context=None):
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in ids)
        holiday_ids = self.pool['hr.holidays'].search(cr, uid, [('employee_id', '=', employee_id),
                                                                ('state', 'in', ['confirm', 'validate1', 'validate']),
                                                                ('holiday_status_id', 'in', ids)
                                                                ], context=context)
        for holiday in self.pool['hr.holidays'].browse(cr, uid, holiday_ids, context=context):
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add':
                status_dict['virtual_remaining_leaves'] += holiday.working_hour
                if holiday.state == 'validate':
                    status_dict['max_leaves'] += holiday.working_hour
                    status_dict['remaining_leaves'] += holiday.working_hour
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.working_hour
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.working_hour
                    status_dict['remaining_leaves'] -= holiday.working_hour
        return result

    def _user_left_days(self, cr, uid, ids, name, args, context=None):
        employee_id = False
        if context and 'employee_id' in context:
            employee_id = context['employee_id']
        else:
            employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
            if employee_ids:
                employee_id = employee_ids[0]
        if employee_id:
            res = self.get_days(cr, uid, ids, employee_id, context=context)
        else:
            res = dict((res_id, {'leaves_taken': 0, 'remaining_leaves': 0, 'max_leaves': 0}) for res_id in ids)
        return res
    
