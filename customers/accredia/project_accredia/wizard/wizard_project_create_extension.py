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


class wizard_project_create_extension(orm.TransientModel):
    _name = 'wizard.project.create.extension'
    _description = 'Wizard Crea Pratica Collegata'

    _columns = {'template_id': fields.many2one('project.project',
                                               string='Template Pratica',
                                               ),
                'department_id': fields.many2one('hr.department',
                                                 string='Dipartimento',
                                                 ),
                'project_type_id': fields.many2one('accreditation.project.type',
                                                   string='Tipo Pratica',
                                                   ),
                }

    def do_create(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        t_analytic_account_id = context.get('parent_id', None)
        t_user_id = context.get('t_user_id ', None)
        if 't_user_id' in context:
            t_user_id = context['t_user_id']
        t_partner_id = context.get('partner_id', None)
        t_certificate_number = context.get('certificate_number', None)
        t_accreditation_due_date = context.get('accreditation_due_date', None)

        project_obj = self.pool.get('project.project')
        for project_data in self.browse(cr, uid, ids, context):
            # recupera dati
            t_template_id = project_data.template_id and project_data.template_id.id or None
            t_project_type_id = project_data.project_type_id and project_data.project_type_id.id or None

            # crea pratica
            context.update({'analytic_project_copy': True,
                            'copy': True,
                            })

            project_obj.copy(cr, uid,
                             t_template_id,
                             default={'state': 'open',
                                      'accreditation_project_type': t_project_type_id,
                                      'parent_id': t_analytic_account_id,
                                      'user_id': t_user_id,
                                      'partner_id': t_partner_id,
                                      'certificate_number': t_certificate_number,
                                      'accreditation_due_date': t_accreditation_due_date,
                                      'child_ids': [],
                                      },
                             context=context)
        return True
