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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class wizard_stock_sheet_result(orm.TransientModel):
    _name = 'wizard.stock.sheet.result'
    _description = 'Print Stock Sheet Result'
    
    def print_report_pdf2(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        t_obj = self.browse(cr, uid, ids[0])
        if(not t_obj.line_ids and len(t_obj.line_ids) < 1):
            raise orm.except_orm(_('Error!'), _('Nessuna riga presente per generazione report'))
        
        datas = {
             'ids': [],
             'model': 'stock.move',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'stock.sheet',
            'datas':datas,
        }

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True), 
        'product_id': fields.many2one('product.product',
                                      'Product',
                                      required=True),
        'warehouse_id': fields.many2one('stock.warehouse',
                                      'Warehouse'),

        'date_from': fields.date('Date From', required=True),
        'date_to': fields.date('Date To', required=True),
        'line_ids': fields.one2many('wizard.stock.sheet.result.line',
                              'result_id',
                              string="Lines",
                              readonly=True)
            }

    def view_new_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'stock_sheet_report_webkit',
                                              'wizard_stock_sheet_view_popup')
        view_id = result and result[1] or False
    
        return {
                      'name': _("Stock Sheet"),
                      'view_type': 'form',
                      'view_mode': 'form',
                      'res_model': 'wizard.stock.sheet',
                      'type': 'ir.actions.act_window',
                      'view_id': view_id,
                      'target': 'new',
                      }
