# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv


class project(osv.osv):
    _inherit = "project.project"

    def _phase_count(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 0)
        phase_ids = self.pool.get('project.phase').search(cr, uid, [('project_id', 'in', ids)])
        for phase in self.pool.get('project.phase').browse(cr, uid, phase_ids, context):
            res[phase.project_id.id] += 1
        return res

    _columns = {
        'phase_ids': fields.one2many('project.phase', 'project_id', "Project Phases"),
        'phase_count': fields.function(_phase_count, type='integer', string="Open Phases"),
    }

    def map_phase(self, cr, uid, old_project_id, new_project_id, context=None):
        """ copy and map phases from old to new project while keeping order relations """
        project_phase = self.pool['project.phase']
        project_task = self.pool['project.task']
        # mapping source and copy ids to recreate m2m links
        phase_ids_mapping = {}
        project = self.browse(cr, uid, old_project_id, context=context)
        if project.phase_ids:
            for phase in project.phase_ids:
                phase_default = {
                    'project_id': new_project_id,
                    'previous_phase_ids': [],
                    'next_phase_ids': [],
                    'task_ids': [],
                }
                # adding relationships with already copied phases
                for previous_phase in phase.previous_phase_ids:
                    if previous_phase.id in phase_ids_mapping:
                        phase_default['previous_phase_ids'].append((4, phase_ids_mapping[previous_phase.id]))
                for next_phase in phase.next_phase_ids:
                    if next_phase.id in phase_ids_mapping:
                        phase_default['previous_phase_ids'].append((4, phase_ids_mapping[next_phase.id]))
                phase_ids_mapping[phase.id] = project_phase.copy(cr, uid, phase.id, phase_default, context=context)
        if project.tasks:
            # if has copied tasks, need to update phase_id
            for task in self.browse(cr, uid, new_project_id, context=context).tasks:
                if task.phase_id and task.phase_id.id in phase_ids_mapping:
                    project_task.write(cr, uid, task.id, {'phase_id': phase_ids_mapping[phase.id]}, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default.update(phase_ids=[])
        new_project_id = super(project, self).copy(cr, uid, id, default, context)
        self.map_phase(cr, uid, id, new_project_id, context=context)
        return new_project_id
