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
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class ProjectType(models.Model):
    _description = "Tipo pratica"
    _name = "accreditation.project.type"

    def _get_empty_dict(self, value):
        if value != 'is_new':
            self.is_new = None
        if value != 'is_extension':
            self.is_extension = None
        if value != 'is_renew':
            self.is_renew = None
        if value != 'is_committees_meeting':
            self.is_committees_meeting = None
        if value != 'is_courses':
            self.is_courses = None
        if value != 'is_conferences':
            self.is_conferences = None
        if value != 'is_meetings':
            self.is_meetings = None
        if value != 'is_experimental_verification':
            self.is_experimental_verification = None

    @api.onchange('is_new')
    def onchange_new(self):
        if self.is_new:
            self._get_empty_dict('is_new')

    @api.onchange('is_extension')
    def onchange_extension(self):
        if self.is_extension:
            self._get_empty_dict('is_extension')

    @api.onchange('is_renew')
    def onchange_renew(self):
        if self.is_renew:
            self._get_empty_dict('is_renew')

    @api.onchange('is_committees_meeting')
    def onchange_committees_meeting(self):
        if self.is_committees_meeting:
            self._get_empty_dict('is_committees_meeting')

    @api.onchange('is_courses')
    def onchange_courses(self):
        if self.is_courses:
            self._get_empty_dict('is_courses')

    @api.onchange('is_conferences')
    def onchange_conferences(self):
        if self.is_conferences:
            self._get_empty_dict('is_conferences')

    @api.onchange('is_meetings')
    def onchange_meetings(self):
        if self.is_meetings:
            self._get_empty_dict('is_meetings')

    @api.onchange('is_experimental_verification')
    def onchange_experimental_verification(self):
        if self.is_experimental_verification:
            self._get_empty_dict('is_experimental_verification')

    name = fields.Char('Description', required=True)
    roles_ids = fields.Many2many(comodel_name='accreditation.roles',
                                 relation='accreditation_project_type_roles',
                                 column1='project_type_id',
                                 column2='role_id',
                                 string='Ruoli')

    is_new = fields.Boolean('Nuovo Accreditamento')
    is_extension = fields.Boolean('Estensione Accreditamento')
    is_renew = fields.Boolean('Rinnovo Accreditamento')
    is_committees_meeting = fields.Boolean('Riunione Comitati')
    is_courses = fields.Boolean('Corsi')
    is_conferences = fields.Boolean('Convegni')
    is_meetings = fields.Boolean('Riunioni Varie')
    is_experimental_verification = fields.Boolean('Accertamenti sperimentali')

    accreditation_request_days = fields.Integer('Giorni anticipo scadenza per invio domanda di accreditamento')

    @api.model
    def create(self, vals):

        t_count = 0

        if 'is_new' in vals and vals['is_new']:
            t_count = t_count + 1

        if 'is_extension' in vals and vals['is_extension']:
            t_count = t_count + 1

        if 'is_renew' in vals and vals['is_renew']:
            t_count = t_count + 1

        if 'is_committees_meeting' in vals and vals['is_committees_meeting']:
            t_count = t_count + 1

        if 'is_courses' in vals and vals['is_courses']:
            t_count = t_count + 1

        if 'is_conferences' in vals and vals['is_conferences']:
            t_count = t_count + 1

        if 'is_meetings' in vals and vals['is_meetings']:
            t_count = t_count + 1

        if 'is_experimental_verification' in vals and vals['is_experimental_verification']:
            t_count = t_count + 1

        if t_count > 1:
            raise except_orm(_('Errore'),
                             _("Non è possibile impostare più di un tipo!"))

        res = super(ProjectType, self).create(vals)

        return res

    @api.multi
    def write(self, vals):

        t_count = 0

        if 'is_new' in vals and vals['is_new']:
            t_count = t_count + 1
        elif 'is_new' not in vals:
            if self.is_new:
                t_count = t_count + 1

        if 'is_extension' in vals and vals['is_extension']:
            t_count = t_count + 1
        elif 'is_extension' not in vals:
            if self.is_extension:
                t_count = t_count + 1

        if 'is_renew' in vals and vals['is_renew']:
            t_count = t_count + 1
        elif 'is_renew' not in vals:
            if self.is_renew:
                t_count = t_count + 1

        if 'is_committees_meeting' in vals and vals['is_committees_meeting']:
            t_count = t_count + 1
        elif 'is_committees_meeting' not in vals:
            if self.is_committees_meeting:
                t_count = t_count + 1

        if 'is_courses' in vals and vals['is_courses']:
            t_count = t_count + 1
        elif 'is_courses' not in vals:
            if self.is_courses:
                t_count = t_count + 1

        if 'is_conferences' in vals and vals['is_conferences']:
            t_count = t_count + 1
        elif 'is_conferences' not in vals:
            if self.is_conferences:
                t_count = t_count + 1

        if 'is_meetings' in vals and vals['is_meetings']:
            t_count = t_count + 1
        elif 'is_meetings' not in vals:
            if self.is_meetings:
                t_count = t_count + 1

        if 'is_experimental_verification' in vals and vals['is_experimental_verification']:
            t_count = t_count + 1
        elif 'is_experimental_verification' not in vals:
            if self.is_experimental_verification:
                t_count = t_count + 1

        if t_count > 1:
            raise except_orm(_('Errore'),
                             _("Non è possibile impostare più di un tipo!"))

        res = super(ProjectType, self).write(vals)

        return res
