# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import orm, fields


class wizard_sale_report_isa(orm.TransientModel):
    
    _name = 'wizard.sale.report.isa'

    def _get_report_datas(self, cr, uid, ids, context=None):
        wizard_form_datas = self.read(cr, uid, ids)[0]
        datas = {
            'ids': [],
            'context': context.get('active_ids', []),
            'form': wizard_form_datas,
        }
        return datas

    _columns = {
        'rows_per_page': fields.integer('Righe per pagina', required=True,),
        'font_description': fields.integer('Dim. font descrizione', required=True,),
        'line_description': fields.boolean('Descrizione da Riga prev.',),
        'font_general': fields.integer('Dim. font intestazione', required=True,),

    }

    def print_report(self, cr, uid, ids, context=None):
        datas = self._get_report_datas(cr, uid, ids, context=context)

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'report_sale_order_isa',
            'datas': datas,
        }

    _defaults = {
        'rows_per_page': 3,
        'font_description': 16,
        'font_general': 14,
        'line_description': True,
    }
