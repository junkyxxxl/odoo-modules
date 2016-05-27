# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.http import request
import openerp.addons.website_sale_delivery.controllers.main


class website_sale(openerp.addons.website_sale_delivery.controllers.main.website_sale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        order = request.website.sale_get_order(context=context)
        acquirer_id = post.get('acquirer_id')
        if acquirer_id:
            acquirer_id = int(acquirer_id)
        if order and acquirer_id:
            request.env['sale.order']._check_acquairer_payment_quotation(order, acquirer_id)
            if acquirer_id:
                return request.redirect("/shop/payment")

        res = super(website_sale, self).payment(**post)
        return res
