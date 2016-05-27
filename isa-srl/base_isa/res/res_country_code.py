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


class res_country_code(orm.Model):

    _name = 'res.country.code'
    _columns = {
                'name': fields.char('Nazione', size=100),
                'code_iso_3166_1': fields.integer('ISO 3166-1'),
                'code_iso_3166_1_alpha_2': fields.char('ISO 3166-1 alpha-2', size=2),
                'code_iso_3166_1_alpha_3': fields.char('ISO 3166-1 alpha-3', size=3),
                }
