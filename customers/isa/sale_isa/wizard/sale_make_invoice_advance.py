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

from openerp.osv import fields, osv


class SaleAdvancePaymentInv(osv.osv_memory):
    _inherit = "sale.advance.payment.inv"

    _columns = {'invoice_date': fields.date('Data',),
                }

    _defaults = {'invoice_date': fields.date.context_today,
                 }

    def _prepare_advance_invoice_vals(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        res = super(SaleAdvancePaymentInv, self)._prepare_advance_invoice_vals(cr, uid, ids, context=context)
        if res and wizard.invoice_date:
            for i in range(0, len(res)):
                if len(res[i]) == 2 and isinstance(res[i][1], dict):
                    res[i][1].update({'date_invoice': wizard.invoice_date,
                                      'registration_date': wizard.invoice_date,
                                      })
        return res

    def create_invoices(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context)
        context.update({'wiz_date': wizard.invoice_date,
                        })
        return super(SaleAdvancePaymentInv, self).create_invoices(cr, uid, ids, context=context)
