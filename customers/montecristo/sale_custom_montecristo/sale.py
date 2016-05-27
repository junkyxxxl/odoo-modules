# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import api

'''
class SaleDocumentType(osv.osv):

    _inherit = 'sale.document.type'

    _columns = {
                'multi_season':fields.boolean('Multi Stagionalità'),
    }
'''    

class date_per_category(osv.osv):
    _name = 'sale.date.category'
    
    _columns = {
                'sale_order_id':fields.many2one("sale.order","Ordine"),
                'category_id':fields.many2one('product.category',string='Gruppo',required=True),
                'delivery_date': fields.date("Data di consegna"),
    }

class discount_per_template(osv.osv):
    _name = 'sale.discount.template'
    
    _columns = {
                'sale_order_id':fields.many2one("sale.order","Ordine"),
                'template_id':fields.many2one('product.template',string='Prodotto',required=True),
                'discount': fields.float('Sconto (%)', digits_compute= dp.get_precision('Discount')),
    }
    

class sale_order_montecristo(osv.osv):
    _inherit = "sale.order"

    def _check_season(self, cr, uid, ids, context=None):
        this = self.browse(cr,uid,ids)
        if not this or not this.season:
            return False
        season_start = this.season.date_start
        season_end = this.season.date_end
        delivery_date = this.delivery_date
        order_line = this.order_line
        
        if  delivery_date < season_start or delivery_date > season_end:
            return False
        
        for line in order_line:
            if line.delivery_date:
                if line.delivery_date < season_start or line.delivery_date > season_end:
                    return False
        return True    

    def _get_qty_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = 0.0
            val = 0.0
            for line in order.order_line:
                val += line.product_uom_qty
            res[order.id] = val
        return res
     
    def _get_historical_pieces(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = 0.0
            val = 0.0
            
            partner_id = order.partner_id
            salesagent_id = order.salesagent_id
            season = order.season
            
            if partner_id and salesagent_id and season and season.previous_ref:
                partner_id = partner_id.id
                salesagent_id = salesagent_id.id
                season = season.previous_ref.id                
                history_obj = self.pool.get('sale.history')
                history_ids = history_obj.search(cr,uid,[('production_id','=',season),('partner_id','=',partner_id),('salesagent_id','=',salesagent_id)])
                if history_ids:
                    history_data = history_obj.browse(cr,uid,history_ids[0])
                    res[order.id] = history_data.pieces
        return res

    def _get_historical_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = 0.0
            val = 0.0
            
            partner_id = order.partner_id
            salesagent_id = order.salesagent_id
            season = order.season
            
            if partner_id and salesagent_id and season and season.previous_ref:
                partner_id = partner_id.id
                salesagent_id = salesagent_id.id
                season = season.previous_ref.id
                history_obj = self.pool.get('sale.history')
                history_ids = history_obj.search(cr,uid,[('production_id','=',season),('partner_id','=',partner_id),('salesagent_id','=',salesagent_id)])
                if history_ids:
                    history_data = history_obj.browse(cr,uid,history_ids[0])
                    res[order.id] = history_data.amount
        return res
    
    def _get_default_season(self, cr, uid, context=None):
        season_ids = self.pool.get('res.family').search(cr,uid,[('current','=',True),('type','=','production')])
        if season_ids:
            return season_ids[-1]
        return  
    
    '''
        Riporta il valore che assegna di default 
    '''
        
    def load_categories_dates(self, cr, uid, ids, context=None):
        sale_data = self.browse(cr,uid,ids[0])
        
        categories_ids = []
        
        previous_categories = []
        permanent_categories = []
        
        for line in sale_data.date_per_category_ids:
            previous_categories.append(line.category_id.id)
        
        for line in sale_data.order_line:
            
            if line.product_id and line.product_id.categ_id:
                if line.product_id.categ_id.parent_id:
                    tmp = line.product_id.categ_id.parent_id.id
                else:
                    tmp = line.product_id.categ_id.id
                    
                permanent_categories.append(tmp)
                    
                if tmp not in previous_categories:
                    categories_ids.append(tmp)
                    
        categories_ids = list(set(categories_ids))

        for date_category_id in sale_data.date_per_category_ids.ids:
            cat_id = self.pool.get('sale.date.category').browse(cr,uid,date_category_id).category_id.id
            if cat_id not in permanent_categories:
                self.pool.get('sale.date.category').unlink(cr,uid,date_category_id)
        
        for category_id in categories_ids:
            self.pool.get('sale.date.category').create(cr,uid, {'sale_order_id':ids[0],'category_id':category_id,'delivery_date':sale_data.delivery_date or None})
        
        return True

    def set_delivery_dates(self, cr, uid, ids, context=None):
        sale_data = self.browse(cr,uid,ids[0])
        sale_line_obj = self.pool.get('sale.order.line')
        
        for date_line in sale_data.date_per_category_ids:
            for line in sale_data.order_line:
                if line.product_id and line.product_id.categ_id:
                    
                    if line.product_id.categ_id.parent_id:
                        tmp = line.product_id.categ_id.parent_id.id
                    else:
                        tmp = line.product_id.categ_id.id
                    
                    if date_line.category_id and tmp == date_line.category_id.id:
                        sale_line_obj.write(cr,uid,line.id,{'delivery_date':date_line.delivery_date})
               
        return True

    def load_template_discounts(self, cr, uid, ids, context=None):
        sale_data = self.browse(cr,uid,ids[0])
        
        templates_ids = []
        
        previous_templates = []
        permanent_templates = []
        
        for line in sale_data.discount_per_template_ids:
            previous_templates.append(line.template_id.id)
        
        for line in sale_data.order_line:
            permanent_templates.append(line.product_id.product_tmpl_id.id)
            if line.product_id and line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.id not in previous_templates:
                templates_ids.append(line.product_id.product_tmpl_id.id)
                
        templates_ids = list(set(templates_ids))

        for discount_template_id in sale_data.discount_per_template_ids.ids:
            tmpl_id = self.pool.get('sale.discount.template').browse(cr,uid,discount_template_id).template_id.id
            if tmpl_id not in permanent_templates:
                self.pool.get('sale.discount.template').unlink(cr,uid,discount_template_id)
        
        for template_id in templates_ids:
            self.pool.get('sale.discount.template').create(cr,uid, {'sale_order_id':ids[0],'template_id':template_id,'discount':0.0})
        
        return True

    def set_discounts(self, cr, uid, ids, context=None):
        sale_data = self.browse(cr,uid,ids[0])
        sale_line_obj = self.pool.get('sale.order.line')
        
        for discount_line in sale_data.discount_per_template_ids:
            for line in sale_data.order_line:
                if line.product_id and line.product_id.product_tmpl_id and discount_line.template_id and line.product_id.product_tmpl_id.id == discount_line.template_id.id:
                    sale_line_obj.write(cr,uid,line.id,{'discount':discount_line.discount})
               
        return True
    
    
    _columns = {
                'date_expected_payment': fields.datetime('Data presunta di incasso'),
                'season':fields.many2one("res.family","Stagionalità",domain="[('type','=','production')]"),
                'delivery_date': fields.date("Data di consegna"),
                'total_qty': fields.function(_get_qty_total, string='Totale Pezzi', store= True, type="float"),
                'historical_pieces': fields.function(_get_historical_pieces, type='float', string='N.Pezzi'),
                'historical_amount': fields.function(_get_historical_amount, type='float', string='Totale Fatturato'),
                'date_per_category_ids':fields.one2many('sale.date.category','sale_order_id','Date di consegna per categoria'),
                'discount_per_template_ids':fields.one2many('sale.discount.template','sale_order_id','Sconti per modello prodotto'),                
                'date_start_payment' : fields.date('Start Payment Date'),
                #'multi_season': fields.related('document_type_id','multi_season', type='boolean', string='Multi Season', store = False),

    }

    _constraints = [
        (_check_season, 'Una o più delle date di consegna specificate non rientrano nel range ammesso dalla stagionalità selezionata.', 
         ['season','delivery_date','order_line']),
    ]


    _defaults = {
                 'season': _get_default_season,
    }

    def onchange_partner_id(self, cr, uid, ids, partner_id, season=None, salesagent_id = None, context=None):
        res = super(sale_order_montecristo,self).onchange_partner_id(cr,uid,ids,partner_id,context=context)
        
        if not 'value' in res:
            res['value'] = {}

        '''Pulisco i campi che vengono resettati dal modulo l10n_it_ddt '''   
    
        if 'goods_description_id' in res['value'] and not res['value']['goods_description_id']:
            del res['value']['goods_description_id']
        if 'carriage_condition_id' in res['value'] and not res['value']['carriage_condition_id']:
            del res['value']['carriage_condition_id']
        if 'transportation_reason_id' in res['value'] and not res['value']['transportation_reason_id']:
            del res['value']['transportation_reason_id']
        if 'transportation_method_id' in res['value'] and not res['value']['transportation_method_id']:
            del res['value']['transportation_method_id']
            
        if season:
            season_id = self.pool.get('res.family').browse(cr,uid,season).previous_ref
            if season_id:
                season = season_id.id
            else:
                season = None                
            
        if partner_id and season and salesagent_id:
            history_obj = self.pool.get('sale.history')
            history_ids = history_obj.search(cr,uid,[('production_id','=',season),('partner_id','=',partner_id),('salesagent_id','=',salesagent_id)])
            if history_ids:
                history_data = history_obj.browse(cr,uid,history_ids[0])
                res['value'].update({'historical_pieces':history_data.pieces, 'historical_amount':history_data.amount})
            else:
                res['value'].update({'historical_pieces':0.0, 'historical_amount':0.0})
        else:
            res['value'].update({'historical_pieces':0.0, 'historical_amount':0.0})
            
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if part and part.country_id:
            incoterm = None
            if part.country_id.code == 'IT':
                incoterm = self.pool.get('stock.incoterms').search(cr,uid,[('code','=','PF')])
            else:
                incoterm = self.pool.get('stock.incoterms').search(cr,uid,[('code','=','EXW')])
            if incoterm:
                res['value'].update({'incoterm':incoterm[0]})
                
        if 'partner_invoice_id' in res['value']:
            if res['value']['partner_invoice_id'] == partner_id:
                parent_id = self.pool.get('res.partner').browse(cr,uid,partner_id,context=context).parent_id
                if parent_id:
                    res['value'].update({'partner_invoice_id':parent_id.id})
        
        return res    

    def onchange_season_salesagent_id(self, cr, uid, ids, partner_id, season, salesagent_id, context=None):
        res = {'value':{}}
        
        if season:
            season_id = self.pool.get('res.family').browse(cr,uid,season).previous_ref
            if season_id:
                season = season_id.id
            else:
                season = None
            
        if partner_id and season and salesagent_id:
            history_obj = self.pool.get('sale.history')
            history_ids = history_obj.search(cr,uid,[('production_id','=',season),('partner_id','=',partner_id),('salesagent_id','=',salesagent_id)])
            if history_ids:
                history_data = history_obj.browse(cr,uid,history_ids[0])
                res['value'].update({'historical_pieces':history_data.pieces, 'historical_amount':history_data.amount})
            else:
                res['value'].update({'historical_pieces':0.0, 'historical_amount':0.0})
        else:
            res['value'].update({'historical_pieces':0.0, 'historical_amount':0.0})
        return res    
    '''
    def onchange_document_type_id(self, cr, uid, ids, document_type_id, context=None):
        res = {'value':{}}
        multi_season = False
        if document_type_id:
            multi_season = self.pool.get('sale.document.type').browse(cr,uid,document_type_id).multi_season            
        res['value'].update({'multi_season':multi_season})
        return res 
    '''
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return self.pool['report'].get_action(cr, uid, ids, 'report_qweb_montecristo.report_sale_order', context=context)

    def print_quotation_preview(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        return self.pool['report'].get_action(cr, uid, ids, 'report_qweb_montecristo.report_sale_order_preview', context=context)
    
    

class sale_history(osv.osv):
    _description = 'Storico Vendite'
    _name = 'sale.history'
    _columns = {
        'production_id': fields.many2one('res.family', 'Stagionalità', domain=[('type','=','production')]),
        'salesagent_id': fields.many2one('res.partner', 'Agente', domain=[('salesagent','=',True)]),
        'partner_id': fields.many2one('res.partner','Cliente',domain=[('customer','=',True)]),
        'pieces': fields.float('N.Pezzi'),
        'amount': fields.float('Totale Fatturato'),
    }
    