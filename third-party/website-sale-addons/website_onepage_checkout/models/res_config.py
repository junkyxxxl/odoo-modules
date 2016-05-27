from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class website_onpage_checkout_settings(osv.osv_memory):
    _inherit = 'website.config.settings'
    _name='website.config.onepage.checkout'

    _columns = {

        'wk_address_panel': fields.boolean(string="Shipping and Billing Information"),
        'wk_address_panel_name': fields.char(string="Panel Name", translate=True),
        'wk_billing_information':fields.boolean(string="Billing Information"),
        'wk_shipping_information':fields.boolean(string="Shipping Information"),
        'wk_orderreview_panel': fields.boolean(string="Order Review and Delivery Option"),
        'wk_orderreview_panel_name': fields.char(string="Panel Name", translate=True),
        'wk_payment_panel': fields.boolean(string="Payment Method"),
        'wk_payment_panel_name': fields.char(string="Panel Name", translate=True),
        'wk_billing_required':fields.many2many('billing.default.fields'),
        'wk_shipping_required':fields.many2many('shipping.default.fields'),
        # 'module_website_terms_conditions':fields.boolean(string="Use Terms and Conditions"),
        # 'module_website_order_notes':fields.boolean(string="Use Order Notes"),
        # 'module_website_country_restriction':fields.boolean(string="Use Checkout Country Restriction"),
    }

    def set_onpage_checkout_configuration(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_address_panel', 
            config.wk_address_panel or True)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_address_panel_name', 
            config.wk_address_panel_name  or 'Billing and Shipping Information')

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_billing_information', 
            config.wk_billing_information or True)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_shipping_information', 
            config.wk_shipping_information or False)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_orderreview_panel', 
            config.wk_orderreview_panel or False)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_orderreview_panel_name', 
            config.wk_orderreview_panel_name  or 'Order Preview and Delivery Method')

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_payment_panel', 
            config.wk_payment_panel or True)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_payment_panel_name', 
            config.wk_payment_panel_name  or 'Payment Option')

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_billing_required', 
            config.wk_billing_required and config.wk_billing_required.ids or False)

        ir_values.set_default(cr, uid, 'website.config.onepage.checkout', 'wk_shipping_required', 
            config.wk_shipping_required and config.wk_shipping_required.ids or False)
       
        return True

    def get_onpage_checkout_configuration(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        wk_address_panel = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_terms_conditions')
        wk_address_panel_name = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_address_panel_name')
        wk_billing_information = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_billing_information')
        wk_shipping_information = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_shipping_information')
        wk_orderreview_panel = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_orderreview_panel')
        wk_orderreview_panel_name = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_orderreview_panel_name')
        wk_payment_panel = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_payment_panel')
        wk_payment_panel_name = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_payment_panel_name')

        wk_billing_required = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_billing_required')

        wk_shipping_required = ir_values.get_default(cr, uid, 'website.config.onepage.checkout', 'wk_shipping_required')
        
        return {'wk_address_panel':wk_address_panel, 'wk_address_panel_name':wk_address_panel_name, 'wk_billing_information':wk_billing_information, 'wk_shipping_information':wk_shipping_information, 'wk_orderreview_panel':wk_orderreview_panel, 'wk_orderreview_panel_name':wk_orderreview_panel_name, 'wk_payment_panel':wk_payment_panel, 'wk_payment_panel_name':wk_payment_panel_name, 'wk_billing_required':wk_billing_required, 'wk_shipping_required':wk_shipping_required}

       

   