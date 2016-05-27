# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp.osv import osv, orm, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from datetime import datetime
from openerp import netsvc

import logging
_logger = logging.getLogger(__name__)

class website_stock_notify(osv.osv):
	_name = "website.stock.notify"
	_inherit = ['mail.thread']

	_columns = {
	'name':fields.char('Name'),
	'email':fields.char('Email'),
	'wk_user':fields.many2one('res.users','User'),
	'wk_product':fields.many2one('product.product','Product'),
	'wk_pageURL':fields.char('PageURl'),
	'state': fields.selection([
		('draft', 'Draft'),
		('cancel','Cancel'),
		('done','Done')
		],'Status', readonly=True),
	}
	_defaults= {
		'state':'draft',
	}

	def create_stock_notify_record(self, cr, uid, product_id, email=False, user_id=False, pageURL=False, context=None):
  		if not context:
  			context={}
  		customer_name = self.pool.get('res.users').browse(cr, uid, user_id).partner_id.name
  		if product_id:
  			self.create(cr, uid, {'name':customer_name,'email':email, 'wk_product':product_id, 'wk_user':user_id,'wk_pageURL':pageURL})
  		return True

	def action_button_cancel(self, cr, uid, ids, context=None):
		self.write(cr ,uid, ids[0],{'state':'cancel'})
		return True

	def action_button_resend(self, cr, uid, ids, context=None):
		self.write(cr ,uid, ids[0],{'state':'draft'})
		return True

	def send_email_button(self, cr, uid, context=None):
		ids = context.get('active_ids', [])
		ir_model_data = self.pool.get('ir.model.data')
		temp_id = ir_model_data.get_object_reference(cr, uid, 'website_stock_notifiy', 'website_stock_notify_email')[1]
		quantities = 0
		if temp_id:
			for res_id in ids:
				self_obj = self.browse(cr, uid, res_id)
				self_id = self_obj.wk_product.id
				quantities = self.pool.get('website').get_product_qty(cr, uid, ids ,self_id, context)
				if quantities > 0:
					if self_obj.state == 'draft':
						mail_confirmed = self.pool.get('email.template').send_mail(cr, uid, temp_id, res_id,force_send = True,context = context)
						if mail_confirmed:
							self.write(cr ,uid, res_id,{'state':'done'})
							partial_id = self.pool.get('stock.notify.wizard').create(cr, uid, {'text':'Mail has been sent Successfully!!!'}, context=context)
							return {'name':"Message",
									'view_mode': 'form',
									'view_id': False,
									'view_type': 'form',
									'res_model': 'stock.notify.wizard',
									'res_id': partial_id,
									'type': 'ir.actions.act_window',
									'nodestroy': True,
									'target': 'new',
									'domain': '[]',
									'context': context
							}
					elif self_obj.state == 'cancel':
						raise osv.except_osv(('Warning'),('Mail cannot be send, you have cancelled it!!'))
					else:
						raise osv.except_osv(('Warning'),('Mail has alerady been sent!!'))
				else:
					raise osv.except_osv(('Warning'),('The quantity of the Product is less than zero, email cannot be send!!!'))
				
	def send_email_cron(self, cr, uid, context=None):

		conf_cron  = self.pool.get('ir.values').get_default(cr, uid, 'website.notifiy.config.settings', 'wk_cron_confirm')
		if conf_cron:
			ids = self.search(cr , uid, [])
			ir_model_data = self.pool.get('ir.model.data')
			temp_id = ir_model_data.get_object_reference(cr, uid, 'website_stock_notifiy', 'website_stock_notify_email')[1]
			quantities = 0
			if temp_id:
				for res_id in ids:
					self_obj = self.browse(cr, uid, res_id)
					self_id = self_obj.wk_product.id
					quantities = self.pool.get('website').get_product_qty(cr, uid, ids ,self_id, context)
					if quantities > 0:
						if self_obj.state != 'done':
							mail_confirmed = self.pool.get('email.template').send_mail(cr, uid, temp_id, res_id,force_send = True,context = context)
							if mail_confirmed:
								self.write(cr ,uid, res_id,{'state':'done'})
								_logger.warning("FORECAST MAIL CONFIRMED TEST")
						else:
							_logger.warning("MAIL ALREADY SENT FORECASTED ")
		else:
			_logger.warning("Mail Can Not Be Send")
								

class website(orm.Model):
	_inherit = 'website'	

	def get_uid(self, cr, uid, ids,context=None):
		if uid:
			return uid

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
