# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ISA s.r.l. (<http://www.isa.it>).
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

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    document_type_id = fields.Many2one('sale.document.type', 'Tipo Documento')
    to_customer = fields.Boolean('A Cliente', default=True)
    to_supplier = fields.Boolean('A Fornitore', default=False)

    @api.multi
    def onchange_customer(self, to_customer):
        if to_customer:
            return {'value': { 'to_supplier': False,}}
        return {}

    @api.multi
    def onchange_supplier(self, to_supplier):
        if to_supplier:
            return {'value': { 'to_customer': False,}}
        return {} 

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/' and vals.get('document_type_id'):
            type_data = self.env['sale.document.type'].browse(vals.get('document_type_id'))
            if type_data.sequence_id:
                # 8.0
                t_new_seq_number = type_data.sequence_id.next_by_id(type_data.sequence_id.id)
                # 9.0
                # t_new_seq_number = type_data.sequence_id.next_by_id()
                vals['name'] = t_new_seq_number or '/'

        return super(SaleOrder, self).create(vals)

    @api.multi
    def action_button_confirm(self):

        assert len(self) == 1, 'This option should only be used for a single id at a time.'

        if self.document_type_id and not self.document_type_id.allow_confirm:
            raise Warning(_('Il tipo documento selezionato non consente la conferma.'))

        return super(SaleOrder, self).action_button_confirm()
