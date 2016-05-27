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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime


class wizard_update_state(orm.TransientModel):
    _name = 'wizard.update.state'
    _description = 'Wizard Update State'

    _columns = {'state': fields.selection([('A', 'Accreditato'),
                                           ('N', 'Non accreditato'),
                                           ('S', 'Sospeso Marchio'),
                                           ], 'Stato',
                                          select=True),
                }

    def do_update(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        t_active_ids = context.get('active_ids', [])
        datetime_today = datetime.strptime(fields.date.context_today(self, cr, uid, context=context), DF)

        if t_active_ids:
            test_list_obj = self.pool.get("accreditation.test.list")
            for wizard_data in self.browse(cr, uid, ids, context):
                t_state = wizard_data.state
                test_list_obj.write(cr, uid,
                                    t_active_ids,
                                    {'state': t_state,
                                     'state_write_date': datetime_today,
                                     'state_write_uid': uid,
                                     },
                                    context)

        return True
