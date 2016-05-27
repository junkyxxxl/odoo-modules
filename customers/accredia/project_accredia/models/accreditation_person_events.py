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


class AccreditationPersonEvents(models.Model):

    _name = "accreditation.person.events"

    name = fields.Char(related='partner_id.name', string='Name', readonly=True)
    project_id = fields.Many2one('project.project', 'Pratica')
    partner_id = fields.Many2one('res.partner', 'Persona Fisica', required=True)
    role_id = fields.Many2one('accreditation.roles', 'Role')
    fnct_email = fields.Char(related='partner_id.email', string='Email', readonly=True)
    fnct_phone = fields.Char(related='partner_id.phone', string='Telefono', readonly=True)
    attendance = fields.Boolean('Presenza')
    unit_id = fields.Many2one('accreditation.units', 'Ref. Unit')

    @api.onchange('partner_id')
    def onchange_partner_id(self):

        res = {'domain': {},
               }

        if not self.partner_id:
            self.role_id = None
            res['domain'].update({'role_id': [('id', 'in', [])], })
            return res

        res['domain'].update({'role_id': [], })
        t_ids = []
        apr_ids = []

        apr_obj = self.env['accreditation.person.roles']

        if self.partner_id.parent_id:
            apr_ids = apr_obj.search([('partner_id', '=', self.partner_id.parent_id.id),
                                      ])
        else:
            apr_ids = apr_obj.search([('partner_id', '=', self.partner_id.id),
                                      ])
        for apr_data in apr_ids:
            if apr_data.role_id:
                t_ids.append(apr_data.role_id.id)

        if t_ids:
            res['domain']['role_id'].append(('id', 'in', t_ids))

        if self.role_id and self.role_id.id not in t_ids:
            self.role_id = None

        return res
