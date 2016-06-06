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


class HrDepartment(models.Model):

    # Department
    _inherit = "hr.department"

    sequence_doclite_in_id = fields.Many2one('ir.sequence', 'Doclite Sequence In')
    sequence_doclite_out_id = fields.Many2one('ir.sequence', 'Doclite Sequence Out')

    sequence_protocol_rv = fields.Many2one('ir.sequence', 'Doclite Sequence Rapporto valutazione')