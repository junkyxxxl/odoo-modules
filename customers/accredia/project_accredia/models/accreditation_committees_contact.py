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

from openerp import fields, models


class AccreditationCommitteesContact(models.Model):
    _description = 'Contatti Comitati'
    _name = 'accreditation.committees.contact'

    sequence = fields.Integer('Sequenza', help="Consente la visualizzazione dei contatti in ordine di sequenza.")
    partner_person_id = fields.Many2one('res.partner',
                                        domain=[('individual', '=', True),
                                                ('parent_id', '!=', None),
                                                ('parent_id', '!=', False)
                                                ],
                                        string='Contatto')
    partner_entity_id = fields.Many2one('res.partner',
                                        domain=[('is_entity', '=', True)],
                                        string='Rappresentanza')
    project_id = fields.Many2one('project.project', string='Pratica')
    register = fields.Boolean('Registro Presenze')

    role_id = fields.Many2one('accreditation.roles', 'Ruolo')

    rel_function = fields.Char(related='partner_person_id.function', string='Posizione Lavorativa')
    rel_email = fields.Char(related='partner_person_id.email', string='Email')
    rel_phone = fields.Char(related='partner_person_id.phone', string='Telefono')

    attendance = fields.Boolean('Presenza')
