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


class AccreditationInstitutionMembers(models.Model):

    _description = "Componenti dei Comitati"
    _name = "accreditation.institution.members"
    _order = "parent_id,sequence,id"
    _rec_name = "parent_id"

    sequence = fields.Integer('Sequenza',
                              default=10,
                              help="Consente la visualizzazione dei contatti in ordine di sequenza.")
    name = fields.Char('Descrizione')
    parent_id = fields.Many2one('res.partner', string='Istituzione')
    partner_person_id = fields.Many2one('res.partner',
                                        string='Contatto')
    partner_entity_id = fields.Many2one('res.partner',
                                        domain=[('is_entity', '=', True)],
                                        string='Rappresentanza')
    register = fields.Boolean('Registro Presenze')
    role_id = fields.Many2one('accreditation.roles', 'Ruolo')
    date_start = fields.Date('Data Inizio')
    date_stop = fields.Date('Data Fine')
    rel_function = fields.Char(related='partner_person_id.function', string='Posizione Lavorativa')
    rel_email = fields.Char(related='partner_person_id.email', string='Email')
    rel_phone = fields.Char(related='partner_person_id.phone', string='Telefono')
    rel_mobile = fields.Char(related='partner_person_id.mobile', string='Mobile')


