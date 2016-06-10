from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class webkul_website_addons(osv.osv_memory):
    _name = 'webkul.website.addons'
    _inherit = 'res.config.settings'

    _columns = {
        #  Product Management
        'module_website_product_pack':fields.boolean(string="Website Product Pack"),
        'module_website_giftwrap':fields.boolean(string="Website Gift Wrap"),
        'module_website_product_label':fields.boolean(string="Product Labels & Stickers"),
        'module_website_multi_image':fields.boolean(string="Website Multi Images"),

        # Return Mangement
        'module_rma': fields.boolean(string="RMA"),

        #Website SEO
        'module_website_seo': fields.boolean(string = "Website SEO"),

        # Stock Management
        'module_website_stock_notifiy':fields.boolean(string="Website Stock Notifiy"),
        'module_website_stock': fields.boolean(string="Website Product Stock"),
       
        # Sales Promotion
        'module_website_voucher':fields.boolean(string="Website Vouchers"),
        'module_website_sales_count':fields.boolean(string="Website Sales Count"),
        'module_wk_review':fields.boolean(string="Product Review"),
        'module_website_product_vote':fields.boolean(string="Product Vote-UP/DOWN"),

        # Product Web page
        'module_website_product_quickview':fields.boolean(string="Website product Quickview"),
        'module_website_product_faq':fields.boolean(string="Frequently Asked Questions (FAQ) on Website`s product"),
        'module_website_qa':fields.boolean(string="Product Q&A"),
        'module_website_product_compare':fields.boolean(string="Website Product Compare"),

        #  Customer info Management
        'module_website_customer_group':fields.boolean(string="Website Customer Group"),
        'module_account_sign_up_details':fields.boolean(string="Date-Of-Birth on SignUp Form"),
        'module_birthday_reminder':fields.boolean(string="Birthday Reminder"),

        # web Page 
        'module_website_onepage_checkout':fields.boolean(string="Website Onepage Checkout"),
        'module_website_guest_checkout':fields.boolean(string="Website Guest Checkout Enable/Disable"),
        'module_website_ajax_login':fields.boolean(string="Website Login/Sign-Up"),
        'module_website_terms_conditions':fields.boolean(string="Website Terms & Conditions"),
        'module_advance_website_settings':fields.boolean(string="Cart Settings"),
        'module_website_wishlist':fields.boolean(string="Product Wishlist"),
        'module_website_order_notes':fields.boolean(string="Website Order Note"),
        'module_website_country_restriction':fields.boolean(string="Website Country Restriction"),
        'module_website_cart_recovery':fields.boolean(string="Abandoned Cart Recovery"),
    }