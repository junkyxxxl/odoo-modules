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

import time

from openerp.osv import fields, osv
from openerp.tools.translate import _

class final_invoice_create_omniapart(osv.osv_memory):
    _inherit = 'hr.timesheet.invoice.create.final'
    _columns = {
        'task': fields.boolean('Attività', help='Il nome dell\'attività a cui è legata la lavorazione sarà mostrato in fattura'),
        'contract': fields.boolean('Contratto', help='Il nome del contratto a cui è legata la lavorazione sarà mostrato in fattura'),
        'date_invoice': fields.date('Data Fattura'),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
