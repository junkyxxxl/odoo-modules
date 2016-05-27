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

class sale_order(orm.Model):
    _inherit = 'sale.order'
    
    _columns = {
                    'template_id' : fields.many2one('product.template','Template'),
                    'value_filter_id' : fields.many2one('product.attribute.value','Filtro'),
                    'show_totals': fields.boolean('Mostra Totali'),
                    'show_uos': fields.boolean('Mostra Seconda Unità di Misura'),
                    'saved': fields.boolean('Saved'),
               }        

    _defaults = {
                 'show_totals':False,
                 'show_uos':False,
                 'saved': True,
    }


    def _check_grid(self, cr, uid, ids, context=None):
        if not self.browse(cr,uid,ids,context=context).saved:
            return False
        return True

    _constraints = [
        (_check_grid, 'Ci sono ancora dati pendenti in griglia. Prima di proseguire col salvataggio dei dati è necessario confermare o annullare quanto inserito nella sezione \'Griglia\'.', 
         ['saved']),
    ]

    def create(self, cr, uid, vals, context=None):
        if vals.get('order_line'):
            if vals['order_line']:
                for i in range(0,len(vals['order_line'])):
                    if vals['order_line'][i][2]!=False:
                        """
                        if vals['order_line'][i][2].has_key('price_subtotal'):
                            del vals['order_line'][i][2]['price_subtotal']
                        if vals['order_line'][i][2].has_key('sequence'):
                            del vals['order_line'][i][2]['sequence']
                        if vals['order_line'][i][2].has_key('state'):
                            del vals['order_line'][i][2]['state']
                        """
                        if vals['order_line'][i][2].has_key('discount'):
                            if vals['order_line'][i][2]['discount']==False:
                                vals['order_line'][i][2]['discount']=0                        
        if 'template_id' in vals:
            vals['template_id']=False
        if 'value_filter_id' in vals:
            vals['value_filter_id'] = False
        return super(sale_order, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        if 'template_id' in vals:
            vals['template_id'] = False       
        if 'value_filter_id' in vals:
            vals['value_filter_id'] = False            
        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    def onchange_template_id(self,cr,uid,ids,template_id,context=None):
        res = {}
        dom = {}
        attr_val_ids = []
        res['value_filter_id']=False        
        tmpl_obj = self.pool.get('product.template')
        attr_val_obj = self.pool.get('product.attribute.value')
        tmpl_data = tmpl_obj.browse(cr,uid,template_id)
        if tmpl_data and tmpl_data.attribute_line_ids:
            for attr in tmpl_data.attribute_line_ids:
                if attr.attribute_id.position == 'row':
                    attr_val_ids = attr.value_ids.ids
            dom = {'value_filter_id':  [('id', 'in', attr_val_ids)]}
        return {'value': res, 'domain': dom}

    def fnct_prova(self, cr, uid, field_name, commands, fields=None, context=None):
        result = []             # result (list of dict)
        record_ids = []         # ids of records to read
        updates = {}            # {id: dict} of updates on particular records

        for command in commands or []:
            if not isinstance(command, (list, tuple)):
                record_ids.append(command)
            elif command[0] == 0:
                result.append(command[2])
            elif command[0] == 1:
                record_ids.append(command[1])
                updates.setdefault(command[1], {}).update(command[2])
            elif command[0] in (2, 3):
                record_ids = [id for id in record_ids if id != command[1]]
            elif command[0] == 4:
                record_ids.append(command[1])
            elif command[0] == 5:
                result, record_ids = [], []
            elif command[0] == 6:
                result, record_ids = [], list(command[2])

        # read the records and apply the updates
        other_model = self.pool[self._fields[field_name].comodel_name]
        for record in other_model.read(cr, uid, record_ids, fields=fields, context=context):

            for field in other_model._columns:
                if field in record and isinstance(record[field],tuple):
                    if len(record[field])>0:
                        record[field] = record[field][0]
                elif field in record and isinstance(record[field],list) and len(record[field])>0:
                    record[field] = [[6,0,record[field]]]              
                         
            result.append(record)

        return result
        
        
class sale_order_line(orm.Model):
    _inherit = 'sale.order.line'    
    '''
    def create(self, cr, uid, values, context=None):

        if values.has_key('company_id'):
            if type(values['company_id']) is list:
                values['company_id'] = values['company_id'][0] 
        
        if values.has_key('order_partner_id'):
            if type(values['order_partner_id']) is list:
                values['order_partner_id'] = values['order_partner_id'][0]
                
        if values.has_key('salesman_id'):
            if type(values['salesman_id']) is list:
                values['salesman_id'] = values['salesman_id'][0]    
   
        if values.has_key('product_id'):
            if type(values['product_id']) is list:
                values['product_id'] = values['product_id'][0]
                
        if values.has_key('product_uom'):
            if type(values['product_uom']) is list:
                values['product_uom'] = values['product_uom'][0]
                
        if values.has_key('tax_id'):
            if type(values['tax_id']) is list:
                if len(values['tax_id'])>0:
                    if type(values['tax_id'][0]) is not list:
                        values['tax_id'] = [[6, False, values['tax_id']]]
                                                
        return super(sale_order_line, self).create(cr, uid, values, context=context)
    '''
    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, price_unit=False, context=None):
        
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        if price_unit in context and context['price_unit']!=0:
            res['value']['price_unit']=context['price_unit']
        return res