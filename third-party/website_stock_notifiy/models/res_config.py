from openerp.osv import fields, osv
from openerp.tools.translate import _

class website_notifiy_config_settings(osv.osv_memory):
	_inherit = 'website.config.settings'
	_name = 'website.notifiy.config.settings'


 ###### These functions set the defaults values in the configuration  they have predefined  syntax...get_default_(field name )#####

	def _get_default_cron(self, cr, uid, ids, context=None):
		ir_model_data = self.pool.get('ir.model.data')
		cron_id = ir_model_data.get_object_reference(cr, uid, 'website_stock_notifiy', 'ir_cron_stock_notify_email_action')[1]
		return cron_id

	def _get_default_email_template(self, cr, uid, ids, context=None):
		ir_model_data = self.pool.get('ir.model.data')
		temp_id = ir_model_data.get_object_reference(cr, uid, 'website_stock_notifiy', 'website_stock_notify_email')[1]
		return temp_id

	_columns = {
        'wk_cron_confirm':fields.boolean('Automatic Email Scheduler'),
        'wk_cron_shedular':fields.many2one('ir.cron','Cron Settings',readonly=True),
        'wk_email_template':fields.many2one('email.template','Email Template',readonly=True)
		}

	_defaults = {
		'wk_cron_shedular':_get_default_cron,
		'wk_email_template':_get_default_email_template,
	}
	def set_default_fields(self, cr, uid, ids, context=None):

		ir_values = self.pool.get('ir.values')
		config = self.browse(cr, uid, ids[0], context)
		ir_values.set_default(cr, uid, 'website.notifiy.config.settings', 'wk_cron_confirm',
		config.wk_cron_confirm)
		return True

	def get_default_fields(self, cr, uid, ids, context=None):
	    ir_values = self.pool.get('ir.values')
	    wk_cron_confirm = ir_values.get_default(cr, uid, 'website.notifiy.config.settings', 'wk_cron_confirm')
	    return {'wk_cron_confirm':wk_cron_confirm}

