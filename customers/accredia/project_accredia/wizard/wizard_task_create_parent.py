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


class wizard_task_create_parent(orm.TransientModel):
    _name = 'wizard.task.create.parent'
    _description = 'Wizard Crea Attivita Genitore'

    _columns = {'task_id': fields.many2one('project.task',
                                           string='Attività Delegata',
                                           ),
                'parent_id': fields.many2one('project.task',
                                             string='Attività Genitore',
                                             ),
                'project_id': fields.many2one('project.project',
                                              string='Pratica',
                                              ),
                }

    def do_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        t_parent_id = context.get('parent_id', None)
        t_task_id = context.get('task_id', None)

        task_obj = self.pool.get('project.task')
        if ids:
            task_obj.write(cr, uid, [t_task_id], {'parent_ids': [(4, t_parent_id)]})

        return True
