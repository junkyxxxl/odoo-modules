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

from openerp import models, fields


class hr_holidays_status_isa(models.Model):
    _inherit = "hr.holidays.status"
    _description = "Leave Type"

    allow_festivities = fields.Boolean(string="Includes days of festivities",
                                       default=False,
                                       help="If checked, the days of festivities are included in the leave type")

    allow_closed_days = fields.Boolean(string="Includes closed days",
                                       default=True,
                                       help="If checked, the closed days are included in the leave type")
