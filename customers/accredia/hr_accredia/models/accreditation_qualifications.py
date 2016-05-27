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


class accreditation_qualifications(orm.Model):

    _name = "accreditation.qualifications"
    _description = "Qualifiche"

    _columns = {
        'name': fields.char('Name',
                            size=40,
                            required=True),
        # Qualification Lines
        'partner_ids': fields.many2many('res.partner',
                                        rel="accreditation_persons_qualifications_rel",
                                        id1='qualification_id',
                                        id2='partner_id',
                                        string='Persone Fisiche'),

        'team_member': fields.boolean('Team Member',
                                      help="Check this box in case is a member of the team."),

        }
