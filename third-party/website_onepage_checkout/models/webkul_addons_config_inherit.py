from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class webkul_website_addons(osv.osv_memory):
    _name = 'webkul.website.addons'
    _inherit = 'webkul.website.addons'

    ##inherit the module for adding config option in webkul_website_addons
   