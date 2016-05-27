# -*- coding: utf-8 -*-
from openerp import models, api


class product_name(models.Model):


    _inherit = ['product.product']


    @api.multi
    @api.depends('default_code', 'name')
    def name_get(self):
        new_res = []
        res = super(product_name,self).name_get()
        for record in res:
            prod = self.browse(record[0])
            if prod.default_code:
                descr = ("[%s] %s") % (prod.default_code, record[1])
                new_res.append((record[0], descr))
            else:
                new_res.append((record[0], record[1]))
        return new_res

