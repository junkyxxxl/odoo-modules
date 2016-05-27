# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime

class stock_transfer_details_mattioli_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    def onchange_package_id(self, cr, uid, ids, product_id, package_id, qty, context=None):
        context = context or {}
        if not package_id or not product_id:
            return {}
        sum = 0;
        res = []
        cr.execute('SELECT qty FROM stock_quant WHERE package_id = %s AND product_id = %s', (package_id,product_id))
        res = cr.fetchall()
        for i in range(0,len(res)):
            sum+=res[i][0]
        if sum<qty:
            warning =   {
                         'title': _('Warning!'),
                         'message': _('La quantita\' desiderata non e\' disponibile nel pacco selezionato.\nLa massima quantita\' disponibile sara\' impostata automaticamente.')
                        }
            return {'warning': warning, 'value': {'quantity': sum}}
        return {}