# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
try:
    import json
except ImportError:
    import simplejson as json

import openerp.http as http
from openerp.http import request
from openerp.addons.web.controllers.main import ExcelExport
import openerp
import xlwt
import StringIO
import openerp.pooler as pooler
from openerp.osv import fields, osv
import os
import zipfile
from datetime import datetime

class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)

    def _getInvPickingQty(self, picking_id, product_id, origin):
        qty = 0
        osv_pool = pooler.get_pool(request.db)
        model = osv_pool.get('stock.picking')  
        inv_stock_pinckings = model.search(request.cr, request.uid, [('origin_picking_id','=',picking_id)])
        for inv_stock_pincking in inv_stock_pinckings:
            inv_stock_pincking_obj = model.browse(request.cr, request.uid, inv_stock_pincking, context=request.context)
            if inv_stock_pincking_obj.state == 'done':
                inv_procurement = inv_stock_pincking_obj.group_id.name
                inv_picking_line_ids = inv_stock_pincking_obj.move_lines
                for inv_picking_line_id in inv_picking_line_ids:
                    inv_move_line_id = osv_pool.get('stock.move').browse(request.cr, request.uid, inv_picking_line_id.id, context=request.context)  
                    inv_product_id = inv_move_line_id.product_id
                    if inv_product_id.id == product_id and inv_procurement == origin:
                        qty += inv_move_line_id.product_uom_qty
        return qty
        

    @http.route('/web/export/xls_picking', type='http', auth='user')
    def export_xls_picking(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])

        rows = data.get('rows', [])
        rows = [int(x) for x in rows]
        
        str_ids =  ",".join(str(x) for x in rows)
        request.cr.execute('SELECT distinct(origin) from stock_picking where id in (' + str_ids + ')')
        origins_list = request.cr.fetchall()
                      
        osv_pool = pooler.get_pool(request.db)
        model = osv_pool.get('stock.picking')
        mov_obj = osv_pool.get('stock.move')
        
        in_memory_zip = StringIO.StringIO()
        zf = zipfile.ZipFile(in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)
       
        datenow = datetime.now()
        
        for origin in origins_list:
            i = 1
            sorigin = origin[0].encode("utf-8")
            stock_picking_ids = model.search(request.cr, request.uid, [('origin','=',sorigin),('id','in',rows)])
            wb = xlwt.Workbook()
            ws = wb.add_sheet('Stock Picking')
            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'dd/mm/yyyy'

            ws.write(0,0,'Numero doc.')
            ws.write(0,1,'Cliente')
            ws.write(0,2,'Data doc.')
            ws.write(0,3,'Codice articolo')
            ws.write(0,4,'Quantita')
            ws.write(0,5,'ID Destinatario')
            ws.write(0,6,'Destinatario')
            ws.write(0,7,'Dest.Riga 1')
            ws.write(0,8,'Dest.Riga 2')
            ws.write(0,9,'Dest.Riga 3')
                        
            for stock_picking_id in stock_picking_ids:           
                stock_picking = model.browse(request.cr, request.uid, stock_picking_id, context=request.context)              
                
                for move_line in stock_picking.move_lines:
                    ret_qty = self._getInvPickingQty(stock_picking_id, move_line.product_id.id,  stock_picking.origin)
                    if (move_line.state not in ['done'] and (move_line.reserved_availability - move_line.extracted_qty - ret_qty != 0)) or (move_line.state in ['done'] and (move_line.product_uom_qty - move_line.extracted_qty - ret_qty != 0)) :
                        ws.write(i, 0, stock_picking.origin + datenow.strftime("%d%m")) 
                        if (stock_picking.partner_id.parent_id):
                            ws.write(i, 1, stock_picking.partner_id.parent_id.property_account_receivable.code[3:])  
                        else:
                            ws.write(i, 1, stock_picking.partner_id.property_account_receivable.code[3:])                              
                        ws.write(i, 2, datetime.strptime(stock_picking.date, "%Y-%m-%d %H:%M:%S"), date_format) 
                        splitcode = move_line.product_id.default_code.split('-')
                        if (len(splitcode)>1):
                            ws.write(i, 3, splitcode[0].encode("utf-8") + '          ' + splitcode[1].encode("utf-8"))
                        else:
                            ws.write(i, 3, move_line.product_id.default_code)
                        
                        if move_line.state not in ['done']:
                            ws.write(i, 4, move_line.reserved_availability - move_line.extracted_qty - ret_qty)
                        else:
                            ws.write(i, 4, move_line.product_uom_qty - move_line.extracted_qty - ret_qty) 
                        ws.write(i, 5, stock_picking.partner_id.id) 
                        ws.write(i, 6, stock_picking.partner_id.name) 
                        ws.write(i, 7, stock_picking.partner_id.street) 
                        if (stock_picking.partner_id.city != False):
                            ws.write(i, 8, str(stock_picking.partner_id.zip) + ' ' + stock_picking.partner_id.city) 
                        else:
                            ws.write(i, 8, str(stock_picking.partner_id.zip))   
                        ws.write(i, 9, stock_picking.partner_id.country_id.name)
                        if move_line.state not in ['done']:
                            mov_obj.write(request.cr, request.uid, move_line.id, {'extracted_qty': move_line.reserved_availability - ret_qty}, context=request.context)
                        else:
                            mov_obj.write(request.cr, request.uid, move_line.id, {'extracted_qty': move_line.product_uom_qty - ret_qty}, context=request.context)
                             
                        i +=1 
            if i == 1:
                ws.write(i, 0, 'NON SONO PRESENTI VARIAZIONI DALL\'ULTIMA ESTRAZIONE')
            output = StringIO.StringIO()
            wb.save(output)
            zf.writestr('Prebolla_' + str(stock_picking.origin) + datenow.strftime("%d%m")  + '.xls', output.getvalue())
        zf.close()
        in_memory_zip.seek(0)
        data = in_memory_zip.read()

        return request.make_response(
            data,
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % 'stock_pickings.zip'),
                ('Content-Type', 'application/zip')
            ],
            cookies={'fileToken': token}
        )
