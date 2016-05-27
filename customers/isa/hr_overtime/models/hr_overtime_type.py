# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models


class hr_overtime_type(models.Model):
    _name = "hr.overtime.type"
    _description = "Overtime Type"

    name = fields.Char('Description', size=64, required=True)
    double_validation = fields.Boolean(string="Apply Double Validation",
                                       default=False,
                                       help="If its True then its overtime type have to be validated by second validator")
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the overtime type without removing it.")
