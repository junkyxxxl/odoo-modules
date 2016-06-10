from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.exceptions import Warning

class website_stock_config_settings(osv.osv_memory):
    _name = 'website.stock.config.settings'
    _inherit = 'website.config.settings'

    _columns = {
        'wk_display_qty': fields.boolean(string="Display Quantity on Product Page"),

        'wk_in_stock_msg': fields.char("In Stock Message",translate=True,
            help="""Out of Stock Message.""", required="1"),

        'wk_out_of_stock_msg': fields.char(" Out of Stock Message",translate=True,
            help="""Out of Stock Message.""", required="1"),

        'wk_stock_type':fields.selection((('on_hand','Quantity on Hand'),('forecasted','Forecasted Quantity'),('outgoing','Quantity On Hand - Outgoing Quantity')),'Stock Type', required="1"),

        'wk_warehouse_type':fields.selection((('all','ALL'),('specific','SPECIFIC')),string="Default Stock Location", required="1" ),

        'wk_stock_location':fields.many2one("stock.location","Stock Location" , domain="[('usage', '=', 'internal')]"),
        
        'wk_warehouse_name':fields.many2one('stock.warehouse',string="Warehouse Name" , readonly="true"),

        'wk_remaining_qty': fields.boolean(string="Show Remaining Quantity"),

        'wk_minimum_qty': fields.integer(string="Show When Qunatity Less Than", required="1"),

        'wk_custom_message': fields.char(string="Custome Message", translate=True, required="1"),

        'wk_deny_order': fields.boolean(string="Deny Order"),
    }

    def onchange_stock_loc(self, cr, uid, ids, wk_stock_location, context=None):
        """
            Returns warehouse id of warehouse that contains location
            :param location: browse record (stock.location)
        """
        vals={}
        wl_obj=self.pool.get("stock.location").browse(cr , uid , wk_stock_location , context=None)
        wh_obj = self.pool.get("stock.warehouse")
        whs = wh_obj.search(cr, uid, [('view_location_id.parent_left', '<=', wl_obj.parent_left), 
                                ('view_location_id.parent_right', '>=', wl_obj.parent_left)], context=context)
        if whs:
            vals['wk_warehouse_name']=whs[0];
        return {'value': vals}

    def set_default_stock_fields(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')
        config = self.browse(cr, uid, ids[0], context)

        ir_values.set_default(cr, uid, 'product.product', 'wk_display_qty', 
            config.wk_display_qty or False)
        ir_values.set_default(cr, uid, 'product.product', 'wk_in_stock_msg', 
            config.wk_in_stock_msg  or 'In Stock!!!')

        ir_values.set_default(cr, uid, 'product.product', 'wk_out_of_stock_msg', 
            config.wk_out_of_stock_msg  or 'Out of Stock!')

        ir_values.set_default(cr, uid, 'product.product', 'wk_stock_type',
            config.wk_stock_type  or 'on_hand')

        ir_values.set_default(cr, uid, 'product.product', 'wk_warehouse_type' , 
            config.wk_warehouse_type  or 'all' )

        ir_values.set_default(cr, uid, 'product.product', 'wk_stock_location',
            config.wk_stock_location and config.wk_stock_location.id or False)

        ir_values.set_default(cr, uid, 'product.product', 'wk_warehouse_name',
            config.wk_warehouse_name and config.wk_warehouse_name.id or False)

        ir_values.set_default(cr, uid, 'product.product', 'wk_remaining_qty', 
            config.wk_remaining_qty or False)

        ir_values.set_default(cr, uid, 'product.product', 'wk_minimum_qty', 
            config.wk_minimum_qty)

        ir_values.set_default(cr, uid, 'product.product', 'wk_custom_message', 
            config.wk_custom_message or 'Last In Stock')

        ir_values.set_default(cr, uid, 'product.product', 'wk_deny_order', 
            config.wk_deny_order or False)

        product=self.pool.get('product.product').search( cr , uid , [] , context=None)
        if config.wk_deny_order:
            self.pool.get('product.product').write(cr, uid , product ,{'wk_order_allow':'deny'} , context=None)
        else:
            self.pool.get('product.product').write(cr, uid , product ,{'wk_order_allow':'allow'} , context=None)

        return True

    def get_default_stock_fields(self, cr, uid, ids, context=None):
        ir_values = self.pool.get('ir.values')

        wk_display_qty = ir_values.get_default(cr, uid, 'product.product', 'wk_display_qty')

        wk_in_stock_msg = ir_values.get_default(cr, uid, 'product.product', 'wk_in_stock_msg')

        wk_out_of_stock_msg = ir_values.get_default(cr, uid, 'product.product', 'wk_out_of_stock_msg')

        wk_stock_type = ir_values.get_default(cr, uid, 'product.product', 'wk_stock_type')

        wk_warehouse_type = ir_values.get_default(cr, uid, 'product.product', 'wk_warehouse_type')

        wk_stock_location = ir_values.get_default(cr, uid, 'product.product', 'wk_stock_location')

        wk_warehouse_name = ir_values.get_default(cr, uid, 'product.product', 'wk_warehouse_name')

        wk_remaining_qty = ir_values.get_default(cr, uid, 'product.product', 'wk_remaining_qty')

        wk_minimum_qty = ir_values.get_default(cr, uid, 'product.product', 'wk_minimum_qty')

        wk_custom_message = ir_values.get_default(cr, uid, 'product.product', 'wk_custom_message')

        wk_deny_order = ir_values.get_default(cr, uid, 'product.product', 'wk_deny_order')

        return {'wk_display_qty':wk_display_qty, 'wk_in_stock_msg':wk_in_stock_msg, 'wk_out_of_stock_msg':wk_out_of_stock_msg, 'wk_stock_type':wk_stock_type ,'wk_warehouse_type':wk_warehouse_type ,'wk_stock_location':wk_stock_location , 'wk_warehouse_name':wk_warehouse_name , 'wk_remaining_qty':wk_remaining_qty ,'wk_minimum_qty':wk_minimum_qty , 'wk_custom_message':wk_custom_message , 'wk_deny_order':wk_deny_order}

       

   