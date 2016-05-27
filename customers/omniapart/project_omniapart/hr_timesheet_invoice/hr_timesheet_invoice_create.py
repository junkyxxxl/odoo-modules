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


from openerp.osv import fields, orm


class hr_timesheet_invoice_create_omniapart(orm.TransientModel):

    _inherit = 'hr.timesheet.invoice.create'

    # VAT X CASH OVERRIDE
    def _get_journal(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        if not user.company_id:
            return False
        company = user.company_id
        if not company.xcash_vat:
            return False
        return company.journal_sale_xcash_id.id

    def _get_fpos(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context)
        if not user.company_id:
            return False
        company = user.company_id
        if not company.xcash_vat:
            return False
        return company.fiscal_position_id.id
    # --- VAT X CASH OVERRIDE

    _columns = {'task': fields.boolean('Attività', help='Il nome dell\'attività a cui è legata la lavorazione sarà mostrato in fattura'),
                'contract': fields.boolean('Contratto', help='Il nome del contratto a cui è legata la lavorazione sarà mostrato in fattura'),
                'date_invoice': fields.date('Data Fattura'),
                'journal_id': fields.many2one('account.journal', 'Journal'),
                'fpos_id': fields.many2one('account.fiscal.position', 'Fiscal Position'),
    }

    _defaults = {'date': 0,
                 'name': 0,
                 'contract': 0,
                 'task': 1,
                 'journal_id': _get_journal,
                 'fpos_id': _get_fpos,
                 }
