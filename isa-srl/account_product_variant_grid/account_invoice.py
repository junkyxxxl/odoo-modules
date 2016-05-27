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
from openerp import api

class account_invoice(orm.Model):
    _inherit = 'account.invoice'
    
    _columns = {
                    'template_id' : fields.many2one('product.template','Template'),
                    'value_filter_id' : fields.many2one('product.attribute.value','Filtro'),
                    'show_totals': fields.boolean('Mostra Totali'),
                    'saved': fields.boolean('Saved'),                    
               }        

    _defaults = {
                 'show_totals':False,
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
        '''
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
        '''                    
        if 'template_id' in vals:
            vals['template_id']=False
        if 'value_filter_id' in vals:
            vals['value_filter_id'] = False
        return super(account_invoice, self).create(cr, uid, vals, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        if 'template_id' in vals:
            vals['template_id']=False
        if 'value_filter_id' in vals:
            vals['value_filter_id'] = False      
        return super(account_invoice, self).write(cr, uid, ids, vals, context=context)

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
            '''
            for field in fields:
                if isinstance(record[field],tuple):
                    if len(record[field])>0:
                        record[field] = record[field][0]
            '''            
            for field in other_model._columns:
                if field in record and isinstance(record[field],tuple):
                    if len(record[field])>0:
                        record[field] = record[field][0]
                elif field in record and isinstance(record[field],list) and len(record[field])>0:
                    record[field] = [[6,0,record[field]]]               
                         
            result.append(record)

        return result
        
    
class account_invoice_line(orm.Model):
    _inherit = 'account.invoice.line'    

    @api.multi 
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        
        res = super(account_invoice_line, self).product_id_change(product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, company_id)
        if price_unit and price_unit!=0:
            res['value']['price_unit']=price_unit
        return res