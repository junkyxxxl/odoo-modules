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

class wizard_product_variant_quantities(orm.Model):
    _name = 'wizard.product.variant.quantities'
    _description = 'Wizard Product Variant Quantities'

    _columns = {
        'template_id': fields.many2one('product.template',
                                   'Template'),
        'location_id': fields.many2one('stock.location',
                                       'Location'),
        'company_id' : fields.many2one('res.company', 
                                       'Company'),
        'stock_quant_ids' : fields.one2many('stock.quant',
                                        'wizard_id', 
                                        'Products'),
    }


    def view_report(self, cr, uid, ids, context=None):
        None
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_company_id(self, cr, uid, ids, company_id=False):
        if company_id==False :
            return
        
        res = []
        
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id=%s AND name LIKE \'Stock\' ORDER BY id', (company_id,))
        r = cr.fetchall()
        y = len(r)
        if r.__len__()>0:
            res=r[0]        
            return {'value': {'location_id': res}}
        
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id=%s ORDER BY id', (company_id,))
        r = cr.fetchall()
        if r.__len__()>0:
            res=r[0]        
            return {'value': {'location_id': res}}
        
        cr.execute('SELECT id FROM stock_location WHERE active = True AND company_id Is NULL ORDER BY id')
        r = cr.fetchall()
        if r.__len__()>0:
            res=r[0]    
            return {'value': {'location_id': res}}
        return