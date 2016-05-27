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

from openerp import fields, models, api


class AccreditationTaskPlan(models.Model):

    _name = "accreditation.task.plan"

    name = fields.Char('Nome')

    task_work_type_id = fields.Many2one('accreditation.task.work.type', string='Tipo Azione', required=True)
    department_id = fields.Many2one('hr.department', string='Dipartimento', required=True)
    stage_id = fields.Many2one('project.task.type', string='Stage', required=True)
    role_id = fields.Many2one('accreditation.roles', string='Ruolo', required=True)

    #days_audit_visit = fields.Float('Giorni Esame Documentale')
    #days_audit_doc_review = fields.Float('Giorni Visita Ispettiva')
    days_audit_visit = fields.Float('Giorni Visita Ispettiva')
    days_audit_doc_review = fields.Float('Giorni Esame Documentale')

    @api.model
    def create(self, vals):

        t_type = self.env['accreditation.task.work.type'].browse(vals['task_work_type_id']).name
        t_department = self.env['hr.department'].browse(vals['department_id']).name
        t_stage = self.env['project.task.type'].browse(vals['stage_id']).name
        t_role = self.env['accreditation.roles'].browse(vals['role_id']).description
        vals['name'] = t_type + '/' + t_department + '/' + t_stage + '/' + t_role

        res = super(AccreditationTaskPlan, self).create(vals)

        return res

    @api.multi
    def write(self, vals):

        t_type = self.task_work_type_id.name
        t_department = self.department_id.name
        t_stage = self.stage_id.name
        t_role = self.role_id.description

        if 'task_work_type_id' in vals and vals['task_work_type_id']:
            t_type = self.env['accreditation.task.work.type'].browse(vals['task_work_type_id']).name
        if 'department_id' in vals and vals['department_id']:
            t_department = self.env['hr.department'].browse(vals['department_id']).name
        if 'stage_id' in vals and vals['stage_id']:
            t_stage = self.env['project.task.type'].browse(vals['stage_id']).name
        if 'role_id' in vals and vals['role_id']:
            t_role = self.env['accreditation.roles'].browse(vals['role_id']).description
        vals['name'] = t_type + '/' + t_department + '/' + t_stage + '/' + t_role

        res = super(AccreditationTaskPlan, self).write(vals)

        return res
