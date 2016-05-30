# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by 73lines
# See LICENSE file for full copyright and licensing details.
from openerp.osv import orm, osv, fields

class website_menu(osv.osv):
    _inherit = "website.menu"
    _columns = {
                'submenu_view':fields.html("SubMenu View"),
                'menu_size':fields.selection([('sm','Small'),('mw','Medium'),
                                              ('fw','Full'),('def','Default')],
                                             string="Menu Size")
                
                }
    
    _defaults = {
                 'menu_size':lambda *a:'def'
                 }
    
    def open_template(self, cr, uid, menu_id, context=None):
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': '/megamenu/edit/%d' % menu_id[0]
        }