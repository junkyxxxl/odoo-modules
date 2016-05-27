# -*- coding: utf-8 -*-
from openerp import models, fields


class res_company(models.Model):

    _inherit = ['res.company']

    family_shipping_notes = fields.Many2many(
        string='Family shipping notes',
        comodel_name='product.family',
        domain=[('type', '=', 'family')],
        context={'default_type': 'family'},
    )
    shipping_notes = fields.Text(
        string='Shipping notes',
        help='Message to print if ddt/invoice contains product with specified family',
    )

    def _print_shipping_notes(self, products_family):
        company_family = self.mapped('family_shipping_notes').mapped('code')
        return any(x in company_family for x in products_family)
