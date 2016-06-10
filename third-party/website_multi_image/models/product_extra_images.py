# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp.osv import osv, fields
from openerp import tools

class product_extra_images(osv.osv):
	_name = 'product.extra.images'
	_description = "Product Extra Images"

	def _get_image(self, cr, uid, ids, name, args, context=None):
		result = dict.fromkeys(ids, False)
		for obj in self.browse(cr, uid, ids, context=context):
			result[obj.id] = tools.image_get_resized_images(obj.image)
		return result

	_columns = {
		'name': fields.char('Image Title',help="A Title shows when you mouse over an image."),
		'image_alt': fields.text('Image ALT Text', help="The alt text within the ALT tag should let the user know"\
			"what an image’s content and purpose are. It will shows if the image doesn't appear on a page. "\
			"Search engines may also use alt text to index your site."),
		'image':fields.binary('Image', required=True),
		'image_small':fields.function(_get_image, type="binary", multi="_get_image",string='Image Small',
            store={
                'product.extra.images': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the product. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
		'template_id':fields.many2one('product.template','Product Template'),
		'sequence':fields.integer('Sequence', required=True)
	}
product_extra_images()

class product_template(osv.osv):
	_inherit = 'product.template'
	_columns = {
		'template_extra_images':fields.one2many('product.extra.images','template_id','Product Extra Images')
	}


