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

from openerp.report import report_sxw
from openerp.tools.translate import _
import os
from datetime import datetime

from webkit_parser_header_fix import HeaderFooterTextWebKitParser


class parser_stock_sheet(report_sxw.rml_parse):
    _name = 'parser.stock.sheet'

    def __init__(self, cr, uid, name, context):

        super(parser_stock_sheet,
              self).__init__(cr, uid, name, context)
        self.cr = cr
        self.uid = uid
        self.filters = []
        self.init_filters = []
        self.start_quantity = 0.0
        self.total_quantity = 0.0
        self.context = context

        company = self.pool.get('wizard.stock.sheet.result').browse(self.cr, self.uid, self.parents['active_id']).company_id
        header_report_name = ' - '.join((_('Estratto Conto Per Partita'), company.name, company.currency_id.name))

        footer_date_time = self.formatLang(str(datetime.today()), date_time=True)
        self.localcontext.update({
            'get_wizard_params':self._get_wizard_params,
            'get_start_quantity':self._get_start_quantity,
            'get_totals_quantity':self._get_totals_quantity,
            'get_start_line':self._get_start_line,
            'get_move_line':self._get_move_line,
            'report_name': _('Scheda Magazzino'),
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'), '[topage]'))),
                ('--footer-line',),
            ],
        })

    def _get_wizard_params(self, date_from, date_to, product_id, warehouse_id):
        if date_from :
            f_date_from = str(date_from) + ' 00:00:00'
            t_date_from = ("date", ">=", f_date_from)
            self.filters.append(t_date_from)
            till = ("date", "<", f_date_from)
            self.init_filters.append(till)
        if date_to :
            t_date_to = ("date", "<=", date_to)
            self.filters.append(t_date_to)
        if product_id :
            t_product_id = ("product_id", "=", product_id)
            self.filters.append(t_product_id)
            self.init_filters.append(t_product_id)
        if warehouse_id :
            t_warehouse_id = ("warehouse_id", "=", warehouse_id)
            self.filters.append(t_warehouse_id)
            self.init_filters.append(t_warehouse_id)

    def _get_start_line(self):
        hrs = self.pool.get('stock.move')
        hrs_list = hrs.search(self.cr, self.uid, self.init_filters)
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)

        stock_picking_obj = self.pool.get('stock.picking')

        for line in move_lines:
            t_picking_id = line.picking_id.id
            t_picking = stock_picking_obj.browse(self.cr, self.uid, t_picking_id)
            t_sign = ''
            if(t_picking and t_picking.picking_type_id):
                t_causes = t_picking.picking_type_id
                t_sign = t_causes.code
            if(t_sign == 'outgoing'):
                self.start_quantity -= float(line.product_qty)
                self.total_quantity = self.start_quantity
            else:
                self.start_quantity += float(line.product_qty)
                self.total_quantity = self.start_quantity
        return move_lines

    def _get_move_line(self):
        hrs = self.pool.get('stock.move')
        hrs_list = hrs.search(self.cr, self.uid, self.filters,
                              order='date')
        move_lines = hrs.browse(self.cr, self.uid, hrs_list)
        
        stock_picking_obj = self.pool.get('stock.picking')

        for line in move_lines:
            t_picking = line.picking_id
            t_sign = ''
            if t_picking and t_picking.picking_type_id:
                t_causes = t_picking.picking_type_id
                t_sign = t_causes.code
            if(t_sign == 'outgoing'):
                self.total_quantity -= float(line.product_qty)
            else:
                self.total_quantity += float(line.product_qty)
        return move_lines

    def _get_start_quantity(self):
        if (self.start_quantity):
            return self.start_quantity
        return 0.0

    def _get_totals_quantity(self):
        return self.total_quantity


HeaderFooterTextWebKitParser('report.stock.sheet',
                             'stock.move',
                             os.path.dirname(os.path.realpath(__file__)) + 
                                                '/stock_sheet.mako',
                             parser=parser_stock_sheet)
