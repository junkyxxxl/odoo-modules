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


class ResCompanyClosedDay(models.Model):
    _name = 'res.company.closed.day'
    _description = 'Closed days'
    _rec_name = 'day'
    _order = 'day'

    day = fields.Selection([(1, 'Monday'),
                            (2, 'Tuesday'),
                            (3, 'Wednesday'),
                            (4, 'Thursday'),
                            (5, 'Friday'),
                            (6, 'Saturday'),
                            (7, 'Sunday')],
                           'Day of the week', required=False)
    company_id = fields.Many2one('res.company', 'Company Reference',
                                 required=True, ondelete="cascade",
                                 select=True, default=lambda self: self.env.user.company_id)
    hours = fields.Float('Number of hours', digits=(4, 2), required=False)
