from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import login_redirect
import logging
from openerp import SUPERUSER_ID
logger = logging.getLogger(__name__)

class Website_stock(http.Controller):

	@http.route('/website/stock_notify/', type='json', auth='public', website=True)
	def stock_notify(self, id, email, pageURL, *args, **kwargs):
		ids = int(id)
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		logger.exception("WEBKUL TEST..USER ID ..%s",uid)
		notify_obj = pool['website.stock.notify']
		record_create = notify_obj.create_stock_notify_record(cr, SUPERUSER_ID, ids, email,uid, pageURL,context=context)
		return record_create
	