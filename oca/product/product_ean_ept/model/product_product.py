from openerp.osv import osv, fields

def __sumDigits(chk, start=0, end=1, step=2, mult=1): 
    return reduce(lambda x, y: int(x)+int(y), list(chk[start:end:step])) * mult
def get_check_digit(chk):
    m0 = 1
    m1 = 3
    t = 10 - (( __sumDigits(chk, start=0, end=12, mult=m0) + __sumDigits(chk, start=1, end=12, mult=m1) ) %10 ) %10 
    if t == 10: 
        return 0 
    else: 
        return t
      
class ProductProduct(osv.osv):
    _inherit = 'product.product'
    def create(self,cr,uid,vals,context=None):
        company_id = vals.get('company_id',self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id)
        if company_id:
            company_obj = self.pool.get('res.company').browse(cr,uid,company_id)
            if company_obj and company_obj.barcode_at_product_create :                
                ean_seq = self.pool.get('ir.sequence').get(cr,uid,'product.product.ean')
                if ean_seq:
                    new_ean13 = "%s%s" %(ean_seq,get_check_digit(ean_seq))
                    if new_ean13 :
                        vals.update({'ean13_ids':[[0, False, {'by_supplier': False, 'name':new_ean13 , 'sequence': 10, 'auto_generated': True}]]})
        
        res=super(ProductProduct, self).create(cr, uid, vals, context)
        return res
    
    def auto_generate_ean13(self,cr,uid,ids,context=None):
        #Max EAN No. is : 
        product_ean13 = self.pool.get('product.ean13')
        ean_seq = self.pool.get('ir.sequence').get(cr,uid,'product.product.ean')
        def check_ean13(ean_seq):
            return product_ean13.search(cr,uid,[('name','=',new_ean13)])
        if ean_seq:
            new_ean13 = "%s%s" %(ean_seq,get_check_digit(ean_seq))
            while check_ean13(new_ean13):
                ean_seq = self.pool.get('ir.sequence').get(cr,uid,'product.product.ean')
                new_ean13 = "%s%s" %(ean_seq,get_check_digit(ean_seq))
            
            ean13_ids = product_ean13.search(cr,uid,[('product_id','in',ids)])
            for ean_obj in product_ean13.browse(cr,uid,ean13_ids):
                product_ean13.write(cr,uid,ean_obj.id,{
                                            'sequence':ean_obj.sequence + 1 if ean_obj.sequence >0 else 2,
                                            })
            vals = {
                    'sequence':1,
                    'name':new_ean13,
                    'product_id':ids[0],
                    'by_supplier':False,
                    }
            product_ean13.create(cr,uid,vals,context=context)
        self.write(cr,uid,ids,{})
        return new_ean13
    
    def _get_main_ean13(self, cr, uid, ids, field_name, arg, context):
        values = {}
        for product in self.browse(cr, uid, ids, context):
            ean13 = False
            if product.ean13_ids:
                # get the first ean13 as main ean13
                ean13 = product.ean13_ids[0].name
            values[product.id] = ean13
        return values

    def _get_ean(self, cr, uid, ids, context=None):
        res = set()
        obj = self.pool.get('product.ean13')
        for ean in obj.browse(cr, uid, ids, context):
            res.add(ean.product_id.id)
        return list(res)

    _columns = {
                'ean13_ids': fields.one2many('product.ean13', 'product_id', 'EAN13',copy=False, domain=[('auto_generated', '=', False)]),
                'main_ean13': fields.function(_get_main_ean13,type='char',size=13,string='Main EAN13',readonly=True,
                                              store={
                                                     'product.product':(lambda self,cr,uid,ids,c={}:ids,['ean13_ids'],20),
                                                     'product.ean13':(_get_ean, ['sequence'], 10)}),}

    # disable constraint
    def _check_ean_key(self, cr, uid, ids):
        "Inherit the method to disable the EAN13 check"
        return True
    
    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

    def search(self, cr, uid, args, offset=0, limit=None,
               order=None, context=None, count=False):
        """overwrite the search method in order to search
        on all ean13 codes of a product when we search an ean13"""

        if filter(lambda x: x[0] == 'ean13', args):
            # get the operator of the search
            ean_operator = filter(lambda x: x[0] == 'ean13', args)[0][1]
            #get the value of the search
            ean_value = filter(lambda x: x[0] == 'ean13', args)[0][2]
            # search the ean13
            ean_ids = self.pool.get('product.ean13').search(
                cr, uid, [('name', ean_operator, ean_value)])           

            #get the other arguments of the search
            args = filter(lambda x: x[0] != 'ean13', args)
            #add the new criterion
            args += [('ean13_ids', 'in', ean_ids)] 
        ret =  super(ProductProduct, self).search(
            cr, uid, args, offset, limit, order, context=context, count=count)
        return ret
