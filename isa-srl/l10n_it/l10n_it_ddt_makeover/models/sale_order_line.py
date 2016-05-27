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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange('delay')
    def onchange_delay(self):
        if self.delay and self.delivery_date:
            t_new_date = datetime.strptime(self.delivery_date[:10], DF) + timedelta(days=self.delay)
            self.delivery_date = str(t_new_date)

    delivery_date = fields.Date('Delivery Date')
    delivery_selection_state = fields.Selection([('C', 'Confirmed'),
                                                 ('S', 'Selected'),
                                                 ('R', 'Created')],
                                                'Delivery Selection State',
                                                default='C')
