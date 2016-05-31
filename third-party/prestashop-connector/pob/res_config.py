from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class pob_config_settings(osv.osv_memory):
    _name = 'pob.config.settings'
    _inherit = 'res.config.settings'
    def _install_modules(self, cr, uid, modules, context):
        """Install the requested modules.
            return the next action to execute

          modules is a list of tuples
            (mod_name, browse_record | None)
        """
        response = super(pob_config_settings, self)._install_modules(cr, uid, modules, context=context)
        if response:
            pob_modules = ''
            if response['tag']=='apps':
                for module in response['params']['modules']:
                    if module.startswith('pob_extension'):
                        pob_modules = pob_modules+ "<h3>&#149; ' %s ' </h3><br />"%(module)
                if pob_modules:
                    message="<h2>Following POB Extensions are not found on your OpenERP -</h2><br /><br />"
                    message=message+pob_modules
                    message=message+'<br /><br />Raise a Ticket at <a href="http://webkul.com/ticket/open.php" target="_blank">Click me</a>'
                    partial_id = self.pool.get('pob.message').create(cr, uid, {'text':message}, context=context)
                    return {
                                'name':_("Message"),
                                'view_mode': 'form',
                                'view_id': False,
                                'view_type': 'form',
                                'res_model': 'pob.message',
                                'res_id': partial_id,
                                'type': 'ir.actions.act_window',
                                'nodestroy': True,
                                'target': 'new',
                                'domain': '[]',
                                'context': context
                            }
        return response

    _columns = {
        'module_pob_extension_stock': fields.boolean("Real-Time Stock Synchronization"),
        'module_pob_extension_multilang': fields.boolean("Multi-Language Synchronization"),

        'pob_delivery_product': fields.many2one('product.product',"Delivery Product",
            help="""Service type product used for Delivery purposes."""),
        'pob_discount_product': fields.many2one('product.product',"Discount Product",
            help="""Service type product used for Discount purposes."""),
    }
    def set_default_fields(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        ir_values.set_default(cr, SUPERUSER_ID, 'product.product', 'pob_delivery_product',
            config.pob_delivery_product and config.pob_delivery_product.id or False)
        ir_values.set_default(cr, SUPERUSER_ID, 'product.product', 'pob_discount_product',
            config.pob_discount_product and config.pob_discount_product.id or False)
        return True
    
    def get_default_fields(self, cr, uid, ids, context=None):
        values = {}
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)
        pob_delivery_product = ir_values.get_default(cr, SUPERUSER_ID, 'product.product', 'pob_delivery_product')
        pob_discount_product = ir_values.get_default(cr, SUPERUSER_ID, 'product.product', 'pob_discount_product')
        return {'pob_discount_product':pob_discount_product,'pob_delivery_product':pob_delivery_product}
pob_config_settings()