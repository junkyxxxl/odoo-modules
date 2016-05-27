# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _

class wizard_product_variant_selection(orm.TransientModel):
    _name = 'wizard.product.variant.selection'
    _description = 'Wizard Product Variant Selection'

    _columns = {
        'template_id': fields.many2one('product.template',
                                   'Template'),
        'location_id': fields.many2one('stock.location',
                                       'Location'),
        'company_id' : fields.many2one('res.company', 
                                       'Company'),
        
    }
    
    def view_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        form = self.read(cr, uid, ids)[0]
        if(form["location_id"]):
            t_location_id = form["location_id"]
        if(form["template_id"]):    
            t_template_id = form["template_id"]
        if(form["company_id"]):    
            t_company_id = form["company_id"]
        
        context.update({
            'default_location_id': t_location_id,
            'default_template_id': t_template_id,
            'default_company_id': t_company_id,
        })
        
        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'stock_quant_product_variant_grid',
                                              'wizard_product_variant_multi_qty_view')
        view_id = result and result[1] or False

        return {
              'name': _("Product Quantities for Template"),
              'view_type': 'form',
              'view_mode': 'form',
              'res_model': 'wizard.product.variant.quantities',
              'type': 'ir.actions.act_window',
              'view_id': view_id,
              'context': context,
              'target': 'new'
              }

    def onchange_company_id(self, cr, uid, ids, company_id=False):
        if company_id==False :
            return
        res = []
        cr.execute('SELECT cid FROM res_company_users_rel WHERE user_id = %s', (uid,))
        r = cr.fetchall()
        rr = []
        for item in r:
            rr.append(item[0])
        if company_id not in rr:
            cmp=r[0]        
        else:
            cmp=(company_id,)
        
        res = []
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id=%s AND name LIKE \'Stock\' ORDER BY id', (cmp[0],))
        r = cr.fetchall()
        y = len(r)
        if r.__len__()>0:
            res=r[0]        
            return {'value': {'company_id': cmp,
                              'location_id': res,
                              }
                    }
        
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id=%s ORDER BY id', (cmp[0],))
        r = cr.fetchall()
        if r.__len__()>0:
            res=r[0]        
            return {'value': {'location_id': res,
                              'company_id': cmp}
                    }
        
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id Is NULL ORDER BY id')
        r = cr.fetchall()
        if r.__len__()>0:
            res=r[0]    
            return {'value': {'location_id': res,
                              'company_id': cmp}
                    }
        return