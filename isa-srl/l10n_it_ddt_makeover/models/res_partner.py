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

from openerp import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier = fields.Boolean('Supplier')
    carrier_flag = fields.Boolean('Carrier', help="Check this box if this contact is a carrier")
    carrier_id = fields.Many2one('delivery.carrier', 'Trasportatore Abituale')
    one_order_one_draft = fields.Boolean('One Order Per Draft', help="If checked one order per draft")
    one_product_one_draft = fields.Boolean('One Product Per Draft', help="if checked one product per draft")
    print_values = fields.Boolean('Print Values', help="if checked print values")
    attach_qc_documents = fields.Boolean('Attach QC Documents', help="If checked attach quality documents ")
    document_copies = fields.Integer('Document Copies', help="Number of document copies")
    packing_notes = fields.Text('Additional Information')

    @api.onchange('carrier_flag')
    def onchange_carrier_flag(self):
        if not self.supplier and self.carrier_flag:
            self.supplier = True
