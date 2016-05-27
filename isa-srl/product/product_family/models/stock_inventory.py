# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class stock_inventory(models.Model):
    _inherit = ['stock.inventory']

    filter = fields.Selection(
        selection='_get_available_filters'
    )

    family_id = fields.Many2one(
        string='Product family',
        comodel_name='product.family',
        domain=[('type', '=', 'family')],
        context={'default_type': 'family'},
    )

    subfamily_id = fields.Many2one(
        string='Product subfamily',
        comodel_name='product.family',
        domain=[('type', '=', 'subfamily')],
        context={'default_type': 'subfamily'},
    )

    def _get_available_filters(self):
        res_filter = super(stock_inventory, self)._get_available_filters()
        res_filter.append(('family', _('Product Family')))
        return res_filter

    @api.model
    def _get_inventory_lines(self, inventory):
        # Se non è stata specificata la famiglia, ritorno direttamente alla funzione base
        if not inventory.family_id:
            return super(stock_inventory, self)._get_inventory_lines(inventory)
        # Altrimenti eseguo la query
        location_obj = self.env['stock.location']
        product_obj = self.env['product.product']
        location_ids = location_obj.search([('id', 'child_of', [inventory.location_id.id])])
        location_ids = [location.id for location in location_ids]
        domain = ' location_id in %s'
        args = (tuple(location_ids),)
        if inventory.family_id:
            domain += ' and pt.family = %s'
            args += (inventory.family_id.id,)
        if inventory.subfamily_id:
            domain += ' and pt.subfamily = %s'
            args += (inventory.subfamily_id.id,)

        self.env.cr.execute('''
           SELECT
            q.product_id as product_id
            , sum(q.qty) as product_qty
            , q.location_id as location_id
            , q.lot_id as prod_lot_id
            , q.package_id as package_id
            , q.owner_id as partner_id
           FROM stock_quant q
           LEFT JOIN product_product p on (q.product_id = p.id)
           LEFT JOIN product_template pt on (p.product_tmpl_id = pt.id)
           WHERE''' + domain + '''
           GROUP BY product_id, location_id, lot_id, package_id, partner_id
        ''', args)

        vals = []
        for product_line in self.env.cr.dictfetchall():
            # replace the None the dictionary by False, because falsy values are tested later on
            for key, value in product_line.items():
                if not value:
                    product_line[key] = False
            product_line['inventory_id'] = inventory.id
            product_line['theoretical_qty'] = product_line['product_qty']
            if product_line['product_id']:
                product = product_obj.browse(product_line['product_id'])
                product_line['product_uom_id'] = product.uom_id.id
            vals.append(product_line)
        return vals
