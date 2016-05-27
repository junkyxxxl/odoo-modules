# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import QueryURL
from openerp.tools.translate import _
from openerp.report import report_sxw

class website_sale(website_sale):
    def set_required_fields(self):
        cr, uid, context = request.cr, request.uid, request.context 
        irmodule_obj = request.registry.get('ir.module.module')
        use_onepage = irmodule_obj.search(cr, uid, [('name','in',['website_onepage_checkout']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
        if not use_onepage:
            self.mandatory_billing_fields = ["name", "phone", "email", "street2", "city", "country_id"]
            self.optional_billing_fields = ["street", "state_id", "vat", "vat_subjected", "zip"]
            self.mandatory_shipping_fields = ["name", "phone", "street", "city", "country_id"]
            self.optional_shipping_fields = ["state_id", "zip"]
        else:
            ##set billing mandaory fields.......
            self.mandatory_billing_fields = ["name", "country_id", "email"]
            self.optional_billing_fields = ["phone",  "street2", "city", "street", "state_id", "vat", "vat_subjected", "zip"]
            billing_required = request.registry.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_billing_required')
            if billing_required:
                billing_obj = request.registry.get('billing.default.fields')
                billing_temp = {"Your Name":"name",
                                "Company Name":"street",
                                "Email":"email",
                                "Phone":"phone" ,
                                "Street":"street2" ,
                                "VAT Number":"vat" ,
                                "City":"city" ,
                                "Zip / Postal Code":"zip" ,
                                "Country":"country_id" ,
                            }
                billing_keys_temp = billing_temp.keys()
                for temp in billing_required:
                    fields_name = billing_obj.browse(cr, SUPERUSER_ID, int(temp), context=context).name
                    if fields_name in billing_keys_temp:
                        self.mandatory_billing_fields.append(billing_temp[fields_name])
                        self.optional_billing_fields.remove(billing_temp[fields_name])

            ##set shipping mandaory fields.......
            self.mandatory_shipping_fields = ["name", "country_id"]
            self.optional_shipping_fields = ["phone", "street", "city", "state_id", "zip"]
            shipping_required = request.registry.get('ir.values').get_default(cr, SUPERUSER_ID, 'website.config.onepage.checkout', 'wk_shipping_required')
            if shipping_required:
                shipping_obj = request.registry.get('shipping.default.fields')
                shipping_temp = {"Name":"name",
                                "Phone":"phone" ,
                                "Street":"street" ,
                                "City":"city" ,
                                "Zip / Postal Code":"zip" ,
                                "Country":"country_id" ,
                            }
                shipping_keys_temp = shipping_temp.keys()
                for temp in shipping_required:
                    fields_name = shipping_obj.browse(cr, SUPERUSER_ID, int(temp), context=context).name
                    if fields_name in shipping_keys_temp:
                        self.mandatory_shipping_fields.append(shipping_temp[fields_name])
                        self.optional_shipping_fields.remove(shipping_temp[fields_name])

    def checkout_form_validate(self, data):
        self.set_required_fields()
        return super(website_sale, self).checkout_form_validate(data)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        cr, uid, context = request.cr, request.uid, request.context
        irmodule_obj = request.registry.get('ir.module.module')
        use_onepage = irmodule_obj.search(cr, uid, [('name','in',['website_onepage_checkout']), ('state', 'in', ['to install', 'installed', 'to upgrade'])], context=context)
        if not use_onepage:
            return super(website_sale, self).checkout() 
      
        order = request.website.sale_get_order(force_create=1, context=context)

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values()
        # getting Payment fuctions value and render with the checkout page
        result = self.payment(post=post)
        values.update(result.qcontext)
     
        values['tax_overview'] = request.env['sale.order'].tax_overview(order)
        return request.website.render("website_onepage_checkout.onepage_checkout", values)

    @http.route(['/shop/onepage/confirm_order'], type='json', auth="public", website=True)
    def onepage_confirm_address(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        """Address controller."""
        # must have a draft sale order with lines at this point, otherwise
        # redirect to shop
        order = request.website.sale_get_order()
        if not order:
            return request.redirect("/shop")
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection
        orm_partner = request.env['res.partner']
        values = self.checkout_values(post)
        values["error"] = self.checkout_form_validate(values["checkout"])
        if values['error']:
            return {
                'success': False,
                'errors': values['error']
            }
        self.checkout_form_save(values["checkout"])
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True, context=context)
        return {
                'success': True,
            }


    def change_delivery_option(self, order, carrier_id):
        """Apply delivery amount to current sale order."""
        if not order or not carrier_id:
            return {'success': False}

        # order_id is needed to get delivery carrier price
        if not request.context.get('order_id'):
            request.context['order_id'] = order.id

        # recompute delivery costs
        request.env['sale.order']._check_carrier_quotation(
            order, force_carrier_id=carrier_id)

        # generate updated total prices
        updated_order = request.website.sale_get_order()

        rml_obj = report_sxw.rml_parse(request.cr, SUPERUSER_ID,
                                       request.env['product.product']._name,
                                       context=request.context)
        price_digits = rml_obj.get_digits(dp='Product Price')

        # get additional tax information
        tax_overview = request.env['sale.order'].tax_overview(updated_order)

        return {
            'success': True,
            'order_total': rml_obj.formatLang(updated_order.amount_total,
                                              digits=price_digits),
            'order_subtotal': rml_obj.formatLang(updated_order.amount_subtotal,
                                                 digits=price_digits),
            'order_total_taxes': rml_obj.formatLang(updated_order.amount_tax,
                                                    digits=price_digits),
            'order_total_tax_overview': tax_overview,
            'order_total_delivery': rml_obj.formatLang(
                updated_order.amount_delivery, digits=price_digits)
        }

    @http.route(['/shop/checkout/delivery_option'], type='json', auth="public", website=True )
    def change_delivery(self , carrier_id=None, **post):
        """
        If delivery method is was changed in frontend.

        Change and apply delivery carrier / amount to sale order.
        """
        order = request.website.sale_get_order()
        return self.change_delivery_option(order, int(carrier_id))

    @http.route()
    def cart(self, **post):
        """
        If one active delivery carrier exists apply this delivery to sale
        order.
        """
        response_object = super(website_sale, self).cart(**post)
        values = response_object.qcontext

        dc_ids = request.env['delivery.carrier'].search(
            [('active', '=', True), ('website_published', '=', True)])
        change_delivery = True
        if dc_ids and len(dc_ids) == 1:
            for line in values['order'].order_line:
                if line.is_delivery:
                    change_delivery = False
                    break
            if change_delivery:
                self.do_change_delivery(values['order'], dc_ids[0])

        return request.website.render(response_object.template, values)