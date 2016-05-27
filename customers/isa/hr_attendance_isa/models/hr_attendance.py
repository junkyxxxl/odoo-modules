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
# from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime
import pytz
from openerp import SUPERUSER_ID


class hr_attendance_isa(orm.Model):
    _inherit = 'hr.attendance'

    _columns = {
        'description': fields.char('Description', size=50, required=False,
                                   help='Specifies the reason for Signing IN/Out.'),
    }

    def _altern_si_so(self, cr, uid, ids, context=None):

        res = True

        if uid != SUPERUSER_ID:
            res = super(hr_attendance_isa, self)._altern_si_so(cr, uid, ids, context)

        return res

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        user_pool = self.pool.get('res.users')
        user = user_pool.browse(cr, SUPERUSER_ID, uid)
        tz = pytz.utc
        if user.partner_id and user.partner_id.tz:
            tz = pytz.timezone(user.partner_id.tz)

        for item in self.browse(cr, uid, ids, context=context):
            if item.name:
                t_date = pytz.utc.localize(datetime.strptime(item.name,
                                                             DATETIME_FORMAT)).astimezone(tz)
                t_date_string = str(t_date)[:19]
                t_name = item.employee_id.name + ' - ' + t_date_string
            res.append((item.id, t_name))
        return res
