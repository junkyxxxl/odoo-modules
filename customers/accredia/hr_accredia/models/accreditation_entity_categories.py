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


class accreditation_entity_categories(orm.Model):

    _name = "accreditation.entity.categories"
    _description = "Categorie degli enti"
    _order = "code"

    _columns = {
        'code': fields.char('Code', size=10, required=True),
        'name': fields.text('Description', required=True),
        'partner_ids': fields.many2many('res.partner',
                                        id1='entity_category_id',
                                        id2='partner_id',
                                        string='Entities'),
        'is_associate': fields.boolean('Socio'),
        'is_organization': fields.boolean('Organismo Istituzionale'),
        }
