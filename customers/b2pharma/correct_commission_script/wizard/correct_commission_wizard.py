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
from openerp.exceptions import Warning

class CorrectCommission(models.TransientModel):
    _name = 'wizard.correct.commission'

    @api.one
    def correct_commission(self):
        
        inv_line_obj = self.env['account.invoice.line']
        inv_obj = self.env['account.invoice']
        company_obj = self.env['res.company']
        
        inv_line_ids = inv_line_obj.search([('commission_perc','=',0.0)])
        inv_ids = []
        
        for line_id in inv_line_ids:
            invoice = line_id.invoice_id
            if invoice.type == 'out_invoice' and invoice.partner_id and invoice.user_id and invoice.user_id.partner_id.salesagent:
                if line_id.product_id and not line_id.product_id.no_commission:
                    
                    salesagent_id = invoice.user_id.partner_id
                    partner = invoice.partner_id
                    partner_id = partner.id
                    company = invoice.company_id
                    product = line_id.product_id   
                    comm_perc = 0.0                                 

                    if salesagent_id.is_overriding:
                        for comm_line in salesagent_id.custom_commission_line_ids:
                            if not comm_line.partner_id or comm_line.partner_id.id == partner_id:
                                if not comm_line.category_id or comm_line.category_id.id == product.categ_id.id:
                                    if not comm_line.template_id or comm_line.template_id.id == product.product_tmpl_id.id:
                                        if not comm_line.product_id or comm_line.product_id.id == product.id:
                                            comm_perc = comm_line.commission_perc
                                            break       
                    
                    if comm_perc == 0.0:                                
                        if company.commission_priority1:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority1, product, partner_id, salesagent_id)
                        if not comm_perc and company.commission_priority2:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority2, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority3:
                            comm_perc = company_obj.get_commission_perc(company.commission_priority3, product, partner_id, salesagent_id)                
                        if not comm_perc and company.commission_priority4:   
                            comm_perc = company_obj.get_commission_perc(company.commission_priority4, product, partner_id, salesagent_id)  
                            
                    if comm_perc:
                        line_id.write({'commission_perc':comm_perc})
                        if line_id.invoice_id not in inv_ids:
                            inv_ids.append(line_id.invoice_id)
                            
            
        for invoice in inv_ids:
            invoice.create_commission_line()
            
        return True