
from openerp import http
from openerp.http import request
from openerp.addons.web.controllers.main import login_redirect
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)

class website_voucher(http.Controller):
	@http.route('/website/voucher/', type='json',  auth='public', website=True)
	def voucher_call(self,secret_code):
		result = {}
		# try:
		cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		voucher_obj = pool['website.voucher']
		wk_order_total=request.website.sale_get_order().amount_total
		result = voucher_obj.validate_voucher(cr, uid, secret_code,wk_order_total, context=context)
		
		if result['status']:
			result1 = request.website.sale_get_order(force_create=1)._add_voucher(result['product_id'], result['value'], result['coupon_id'], result['coupon_name'],result['total_available'],wk_order_total,result['voucher_val_type'])
			if not result1['status']:
				result.update(result1)
			request.session['secret_key_data']={'coupon_id':result['coupon_id'],'total_available':result['total_available'],'wk_voucher_value':result['value'],'voucher_val_type':result['voucher_val_type']}
			
		return result


	@http.route(['/shop/cart/voucher_remove/<temp>'], type='http', auth="public",  website=True)
	def remove_voucher(self,temp='0'):
		cr, uid, context, pool = request.cr, request.uid, request.context,request.registry
		line_id=int(temp)
		voucher_obj = pool['website.voucher']
		sale_order_obj = request.registry.get('sale.order.line')
		product_id = request.registry.get('website').wk_get_default_product(cr,SUPERUSER_ID)
		secret_code=request.session.get('secret_key_data')
		if secret_code['total_available'] != -1:
			voucher_obj.return_voucher(cr,SUPERUSER_ID,secret_code['coupon_id'])
		if product_id and line_id:
			sale_order_obj.unlink(cr, SUPERUSER_ID, [line_id], context=context)
		return request.redirect("/shop/cart/")
