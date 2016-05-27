# -*- coding: utf-8 -*-
# © <2016> <Isa>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api


class productTemplate(models.Model):
    _inherit = ['product.template']

    price_history_count = fields.Integer(
        string='# of Price History',
        compute='_price_history_count'
    )

    price_history_ids = fields.One2many(
        'product.price.history',
        'product_template_id',
        'Product price History'
    )

    @api.depends('price_history_ids')
    def _price_history_count(self):
        for record in self:
            print self.env.context
            company_id = self.env.user.company_id.id
            prices_history = self.env['product.price.history'].search([
                ('company_id', '=', company_id),
                ('product_template_id', '=', record.id)
            ])
            self.price_history_count = len(prices_history)
