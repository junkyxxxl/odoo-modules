from openerp.models import Model
from openerp import SUPERUSER_ID
from openerp.osv import osv
from openerp.tools.safe_eval import safe_eval
from openerp import api, fields, models, _,tools

class object_carousel_data(osv.AbstractModel):
    _name = 'object.carousel.data'
    _carousel_data = True
    
#     @tools.ormcache_context('filter_id', keys=('website_id',))
    def eval_filter_data(self,cr,uid,filter_id,context=None):
        if context is None:
            context={}
        res = {'domain':[],'model':self._name,'order':False}
        if filter_id:
            filter_data = self.pool.get('ir.filters').browse(cr,SUPERUSER_ID,filter_id,context=context)
            localdict = {'uid':uid}
            res['domain'] = safe_eval(filter_data.domain,localdict)
            res['model'] = filter_data.model_id
            res['name']=filter_data.name
#             order_by = safe_eval(filter_data.sort)
#             if order_by:
#                 for ele in order_by:
#                     if ele.startswith("-"):
#                         ele=ele.replace("-",'')
#                         order = ele + " desc, "+ order
#                     else:
#                         order = ele + " asc, " + order
#                 res['order']=order
        return res
    
#     @tools.ormcache_context('filter_id','limit', keys=('website_id',))
    def get_objects_for_carousel(self,cr,uid,filter_id,limit,context=None):
        filter_data = self.eval_filter_data(cr, uid, filter_id, context)
        filter_model_pool = self.pool.get(filter_data['model']) 
        if filter_data:
            object_ids = filter_model_pool.search(cr,SUPERUSER_ID,filter_data['domain'],
                                                                 limit=limit, order=filter_data['order'],context=context)
            if object_ids:
                objects = filter_model_pool.browse(cr,SUPERUSER_ID,object_ids,context=context)
            else:
                objects = []
            return {'objects':objects,'name':'name' in filter_data and filter_data['name'] or _("All")}



class res_partner(models.Model):
    _inherit = ["res.partner","object.carousel.data"]