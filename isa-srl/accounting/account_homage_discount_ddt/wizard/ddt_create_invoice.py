# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, fields
from openerp.tools.translate import _
from openerp.exceptions import Warning


class DdTCreateInvoiceDiscount(models.TransientModel):

    _inherit = "ddt.create.invoice"

    @api.multi
    def create_invoice(self):
        ddt_model = self.env['stock.ddt']
        picking_pool = self.pool['stock.picking']
        ddts = ddt_model.browse(self.env.context['active_ids'])

        invoice_list = []
        t_ddt_dict = {} # raggruppamento per fatture

        # struttura dati per raggruppamento

        for ddt in ddts:
            if ddt.ddt_lines \
                and ddt.ddt_lines[0].procurement_id \
                    and ddt.ddt_lines[0].procurement_id.sale_line_id \
                        and ddt.ddt_lines[0].procurement_id.sale_line_id.order_id \
                            and ddt.ddt_lines[0].procurement_id.sale_line_id.order_id.global_discount_lines:
                key = ()
                for line in ddt.ddt_lines[0].procurement_id.sale_line_id.order_id.global_discount_lines:
                    key+= (line.name.id,line.value)
            else:
                key = (None)

            if key not in t_ddt_dict:
                t_ddt_dict[key] = []
            t_ddt_dict[key].append(ddt.id)           
                              

        for t_key in t_ddt_dict:
            ddt_list = t_ddt_dict[t_key]

            invoices = super(DdTCreateInvoiceDiscount,self.with_context(active_ids=ddt_list)).create_invoice()
            
            if invoices and 'domain' in invoices and invoices['domain'] and len(invoices['domain'][0]) == 3 and invoices['domain'][0][2]:
                invoice_list += invoices['domain'][0][2]

        mod_obj = self.env['ir.model.data']

        search_view_res = mod_obj.get_object_reference('account', 'view_account_invoice_filter')
        search_view_id = search_view_res and search_view_res[1] or False

        form_view_res = mod_obj.get_object_reference('account', 'invoice_form')
        form_view_id = form_view_res and form_view_res[1] or False

        return  {
            'domain': [('id', 'in', invoice_list)],
            'name': 'Fatture da DDT',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
        }
