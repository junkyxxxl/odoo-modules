# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class sale_order_makeover(osv.osv):
    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        if context is None:
            context = {}
        invoice_vals = super(sale_order_makeover, self)._prepare_invoice(cr, uid, order, lines, context=context)
        if invoice_vals:
            jour_id = order.company_id.sale_journal_default and order.company_id.sale_journal_default.id            
            if jour_id:
                invoice_vals.update({'journal_id': jour_id})
        return invoice_vals