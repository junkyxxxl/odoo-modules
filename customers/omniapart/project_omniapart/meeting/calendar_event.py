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

from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


class calendar_meeting(orm.Model):

    _inherit = 'calendar.event'

    _columns = {
        'task_id': fields.many2one('project.task', 'Attività'),
    }

    def write(self, cr, uid, ids, vals, context=None):

        for id in self.browse(cr,uid,ids):
            if 'start_datetime' in vals or 'stop_datetime' in vals or 'allday' in vals or 'user_id' in vals:
                if 'update_meeting' not in context or not context['update_meeting']:
                    for id in self.browse(cr,uid,ids):
                        if id.task_id:
                            raise osv.except_osv(_('Error!'),
                                             _('Non puoi modificare direttamente i meeting derivanti da attività!'))

            super(calendar_meeting, self).write(cr, uid, id.id, vals, context=context)
        return

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        if 'delete_meeting' not in context or not context['delete_meeting']:
            for id in self.browse(cr,uid,ids):
                if id.task_id:
                    raise osv.except_osv(_('Error!'),
                                     _('Non puoi cancellare direttamente i meeting derivanti da attività!'))

        res = super(calendar_meeting, self).unlink(cr, uid, ids, context=context)
        return res
