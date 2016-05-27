# -*- coding: utf-8 -*-
from openerp import models, fields, api

class stock_picking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def action_invoice_create(self, journal_id, group=False, type='out_invoice'):
        invoice_id = super(stock_picking, self).action_invoice_create(journal_id, group, type)
        invoice_obj = self.env['account.invoice'].browse(invoice_id)
        
        sale_order_line_ids = []
        
        for picking in self:
            if picking.sale_id:
                for id in picking.sale_id.order_line.ids:
                    sale_order_line_ids.append(id)
        
                sale_order_line_obj = self.env['sale.order.line'].browse(sale_order_line_ids)
        
                for sale_order_line in sale_order_line_obj:
                    #TODO da verificare con fatture multiple sullo stesso picking
                    product_tmpl_id = sale_order_line.product_id.product_tmpl_id.id
                    kit_obj = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_tmpl_id)])
                    #Controllo se il prodotto associato alla sale_order_line è un kit: se si,
                    #prendo le linee di fattura relative alla sale_order_line e:
                    #setto sulla prima il product_id = sale_order_line.product_id (write)
                    #cancello le altre linee (unlink)
                    if kit_obj:
                        number_of_invoices = len(sale_order_line.invoice_lines)
                        i = 1
                        sale_order_line.invoice_lines[0].product_id = sale_order_line.product_id.id
                        sale_order_line.invoice_lines[0].name = sale_order_line.name
                        sale_order_line.invoice_lines[0].price_unit = sale_order_line.price_unit
                        #Cerco la quantità del primo prodotto sulla invoice_line nella bom_obj
                        qty_element_kit = self.env['mrp.bom.line'].search([('bom_id', '=', kit_obj.id)])[0].product_qty
                        #setto la quantità della linea di fattura = old_qty_invoice_line / numero di elementi del kit di queto prodotto
                        sale_order_line.invoice_lines[0].quantity = sale_order_line.invoice_lines[0].quantity / qty_element_kit
                        sale_order_line.invoice_lines[0].discount1 = sale_order_line.discount1
                        sale_order_line.invoice_lines[0].discount2 = sale_order_line.discount2
                        sale_order_line.invoice_lines[0].discount3 = sale_order_line.discount3
                        #Controllo se nel kit è stato settato il conto
                        property_account = sale_order_line.product_id.product_tmpl_id.property_account_income
                        if property_account:
                            sale_order_line.invoice_lines[0].account_id = property_account
        
                        while(i < number_of_invoices):
                           sale_order_line.invoice_lines[i].unlink()
                           i = i+1
        return invoice_id




