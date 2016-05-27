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

from openerp import models, fields, api, _
from datetime import date, datetime
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.exceptions import ValidationError
import base64
from dateutil.relativedelta import relativedelta

class wizard_sale_print_bill(models.TransientModel):

    _name = 'wizard.sale.print.bill'
    _description = 'Print Bill from Sale Order'

    def _get_default_payment(self):
        if not self.sale_id and not 'default_sale_id' in self._context:
            return 0
        if self.sale_id:
            return self.sale_id.amount_total
        return self.env['sale.order'].browse(self._context['default_sale_id']).amount_total

    sale_id = fields.Many2one('sale.order', string='Sale Order')
    payment_method = fields.Selection([('online','Online'),('cash','Cash')], string="Payment Method", default='cash', )
    payment_amount = fields.Float(string="Payment", digits_compute= dp.get_precision('Account'), default=_get_default_payment)
    discount_amount = fields.Float(string="Discount", digits_compute= dp.get_precision('Account'), )
    rest = fields.Float(string="Rest", digits_compute= dp.get_precision('Account'), )

    @api.onchange('payment_method','payment_amount','discount_amount')
    def onchange_to_rest(self):
        if self.payment_method == 'cash':
            self.rest = self.payment_amount - self.sale_id.amount_total + self.discount_amount
        else:
            self.rest = 0
        
    @api.multi
    def _write_bill(self, sale):
        bill_file = open(sale.name+'.txt','w')
        bill_txt = ''
        
        bill_file.write('1322\n')
        bill_txt += '1322\n'
        for line in sale.order_line:
            linestring = ('1325;')
            
            priceunit_string = ("%.2f" % line.price_subtotal).replace('.',',')
            priceunit_string = priceunit_string.ljust(len(priceunit_string)+1,' ')
            priceunit_string = priceunit_string.rjust(11, ' ')
            
            linestring += priceunit_string +';'
            
            descriptorstring = line.name.ljust(28,' ')
            
            linestring += descriptorstring[0:28]+';'
            
            if line.tax_id:
                #if line.tax_id[0].amount:
                linestring += str(int(line.tax_id[0].amount*100)).rjust(2,'0')[0:2]+';'
                #else:
                #    linestring += '  ;'
            else:
                linestring += '  ;'
            
            if line.product_uom_qty > 1:
                qtystring = "%.2f" % line.product_uom_qty
                qtystring = qtystring.rjust(10,' ') 
                
                pricestring = ("%.2f" % (line.price_subtotal/line.product_uom_qty)).replace('.',',')
                pricestring = pricestring.rjust(10,' ')
                
                linestring = linestring + qtystring+'X'+pricestring+';'
            
            linestring+='\n'
            bill_file.write(linestring)
            bill_txt+=linestring

        bill_file.write('1332\n')
        bill_txt+='1332\n'        
        
        if self.payment_method == 'cash':
            if self.discount_amount:
                discount_line = '1327;'
                discounttotal_string = ("%.2f" % self.discount_amount).replace('.',',')
                discounttotal_string = discounttotal_string.ljust(len(discounttotal_string)+1,' ')
                discounttotal_string = discounttotal_string.rjust(11, ' ')
                discount_line+=discounttotal_string+';\n'                
                bill_file.write(discount_line)      
                bill_txt+= discount_line     
            payment_amount = self.payment_amount
        else:
            payment_amount = sale.amount_total
            
        if payment_amount != sale.amount_total:
            total_string = "1329;"
            pricetotal_string = ("%.2f" % payment_amount).replace('.',',')
            pricetotal_string = pricetotal_string.ljust(len(pricetotal_string)+1,' ')
            pricetotal_string = pricetotal_string.rjust(11, ' ')
            total_string += pricetotal_string + ';\n'
        else:
            total_string = "1329\n"
        bill_file.write(total_string)
        bill_txt+=total_string
                 
        bill_file.write('1323\n')
        bill_file.write('912;1')
        
        bill_txt+='1323\n'+'912;1'
        
        bill_file.close()
        
        vals = {
                'name':'bill_'+sale.name,
                'datas': base64.encodestring(bill_txt),
                'datas_fname': bill_file.name,
                'res_model': 'sale.order',
                'res_id': sale.id,
                'file_type': 'text/plain',
                'type': 'binary',
            }
        self.env['ir.attachment'].create(vals)
        
        return bill_file
        
        
                    
    @api.multi
    def print_bill(self):

        self.sale_id.write({'picking_policy':'one'})
        self.sale_id.action_button_confirm()
        
        pick_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        quant_obj = self.env['stock.quant']
        trans_obj = self.env['stock.transfer_details']
        
        for picking in self.sale_id.picking_ids:
            
            picking.action_assign()
            if picking.state not in ['partially_available','assigned']:
                picking.force_assign()
            
            ctx = {}
            for item in self._context.items():
                ctx[item[0]] = item[1]
            ctx.update({'active_ids':[picking.id], 'active_model':'stock.picking'})
            created_id = trans_obj.with_context(ctx).create({'picking_id': picking.id or False})
            created_id.do_detailed_transfer()                   
            
            picking.write({'invoice_state':'invoiced'})
        
        bill_file = self._write_bill(self.sale_id)

        
            
        return        
        