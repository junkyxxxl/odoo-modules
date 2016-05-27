from openerp.osv import fields,osv
from openerp.tools.translate import _

	
class wk_wizard_message(osv.osv_memory):
	_name = "wk.wizard.message"
	_columns={
			'text': fields.text('Message'),
	         }
wk_wizard_message()
