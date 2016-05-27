# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _

class stock_notify_wizard(osv.osv_memory):
	_name = 'stock.notify.wizard'
			
	_columns = {
		'text':fields.text("Message"),
	}
