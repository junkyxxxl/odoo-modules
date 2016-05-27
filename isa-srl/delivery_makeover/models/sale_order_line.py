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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import datetime, timedelta


class sale_order_line_delivery_makeover(orm.Model):
    _inherit = "sale.order.line"

    def onchange_delay(self, cr, uid, ids, delay, delivery_date, context=None):
        if(delay and delivery_date):
            t_new_date = datetime.strptime(delivery_date[:10], DF) + timedelta(days=delay)
            return {
                    'value': {'delivery_date': str(t_new_date), }
                    }
        return {'value': {}
                }

    _columns = {'delivery_date': fields.date('Delivery Date'),
                'delivery_selection_state': fields.selection([('C', 'Confirmed'),
                                                              ('S', 'Selected'),
                                                              ('R', 'Created')],
                                                             'Delivery Selection State'),
                }

    _defaults = {'delivery_selection_state': 'C'
                 }
