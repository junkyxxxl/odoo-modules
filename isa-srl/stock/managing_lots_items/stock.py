# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date, datetime

class stock_quant(models.Model):

    _inherit = 'stock.quant'

    #se la removal_date del lotto è minore della data corrente o vuota non lo considero nel picking
    @api.model
    def quants_get(self, location, product, qty, domain=None, restrict_lot_id=False, restrict_partner_id=False):
        if location.removal_strategy_id.method == 'fefo' and (product.track_incoming or product.track_incoming or product.track_all):
            lot_ids = self.env['stock.production.lot'].search([('product_id','=',product.id),'|',('use_date','=',None),('use_date','>=', datetime.strftime(datetime.today(), "%Y-%m-%d"))])
            lot_domain = []
            for lot_id in lot_ids:
                lot_domain.append(lot_id.id)
            domain += [('lot_id', 'in', (lot_domain))]
        return super(stock_quant, self).quants_get(location, product, qty, domain, restrict_lot_id=False, restrict_partner_id=False)

    @api.model
    def apply_removal_strategy(self, location, product, qty, domain, removal_strategy):
        if removal_strategy == 'fefo':
            order = 'removal_date, package_id,id'
            return self._quants_get_order(location, product, qty, domain, order)
        return super(stock_quant, self).apply_removal_strategy(location, product, qty, domain, removal_strategy)
