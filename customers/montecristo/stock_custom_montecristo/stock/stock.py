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

from openerp import api
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from datetime import datetime


class stock_reservation_availability(osv.osv):

    _name = 'stock.reservation.availability'
    _description = "Product Availability"      

    _columns = {
                'reservation_id': fields.many2one('stock.template.reservation','Reservation', select=True),
                'product_id': fields.many2one('product.product','Product', select=True),
                'available_qty': fields.float('Available Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
                'external_available_qty': fields.float('Available in Other Location', digits_compute=dp.get_precision('Product Unit of Measure')),
                'required_qty': fields.float('Required Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
                'assigned_qty': fields.float('Assigned Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
                'original_assigned_qty': fields.float('Original Assigned Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
                'original_available_qty': fields.float('Original Available Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
                'residual': fields.float('Residual', digits_compute=dp.get_precision('Product Unit of Measure')),
    }

class stock_reservation_product(osv.osv):
    
    _name = 'stock.reservation.product'
    _description = 'Reservations'

    def _get_invisibility(self, cr, uid, ids, field_name, arg, context=None):

        r = {}
        for id in ids:
            line = self.browse(cr, uid, id)
            if line.reservation_id and line.reservation_id.location_id and line.location_id and line.location_id.id == line.reservation_id.location_id.id:
                r[id] = False
            elif line.move_id.reserved_availability == 0.0:
                r[id] = False
            else:
                r[id] = True
        return r

    _columns = {
                'reservation_id': fields.many2one('stock.template.reservation','Reservation', select=True),
                'move_id': fields.many2one('stock.move','Movement', select=True),

                'is_invisible' : fields.function(_get_invisibility, type='boolean', string='Invisible', store=False),
                
                'order_id': fields.related('move_id','procurement_id','sale_line_id','order_id', type='many2one', relation='sale.order', string='Sale Order', store=True),
                'stock_number': fields.related('move_id','procurement_id','sale_line_id','order_id','stock_number_txt', type='char', string = 'Stock Number', store = True),
                'partner_id': fields.related('move_id','partner_id', type='many2one', relation='res.partner', string='Partner', store = True),
                'picking_id': fields.related('move_id','picking_id', type='many2one', relation='stock.picking', string='Picking', store = True),
                'product_id': fields.related('move_id','product_id', type='many2one', relation='product.product', string='Product', store = True),
                'requested_qty': fields.related('move_id','product_qty', type='float', string = 'Requested Quantity', store = True),
                'location_id': fields.related('move_id','location_id', type='many2one', relation='stock.location', string='Location', store = False),
                
                'previously_reserved_qty': fields.float('Already Reserved Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),                
                'difference': fields.float('Difference', digits_compute=dp.get_precision('Product Unit of Measure')),
                'reserved_qty': fields.float('Reserved Quantity', digits_compute=dp.get_precision('Product Unit of Measure'))
    }

    def onchange_reservation(self, cr, uid, ids, res, pre, context=None):
        val = res - pre
        return {'value':{'difference':val}}
        
class stock_template_reservation(osv.osv):
    
    _name = 'stock.template.reservation'
    _description = "Scalature e Divisioni"
    _order = 'date_confirmation desc, product_tmpl_id, id'    

    def _get_res_lines(self, cr, uid, ids, fields, args, context=None):
        line_obj = self.pool.get('stock.reservation.product')
        res = {}
        for reservation in self.browse(cr, uid, ids):
            args = [('reservation_id', '=', reservation.id)]
            if reservation.partner_id:
                args.append(('partner_id','=',reservation.partner_id.id))
            if reservation.order_id:
                args.append(('order_id','=',reservation.order_id.id))
            line_ids = line_obj.search(cr, uid, args, context=context)
            res[reservation.id] = line_ids
        return res
    
    def _set_res_lines(self, cr, uid, id, name, value, inv_arg, context):
        line_obj = self.pool.get('stock.reservation.product')
        for line in value:
            if line[0] == 1: # one2many Update
                line_id = line[1]
                line_obj.write(cr, uid, [line_id], line[2])
        return True

    def _get_partners(self, cr, uid, ids, name, args, context=None):
        result = {}
        for reservation in self.browse(cr, uid, ids, context=context):
            res = []
            cr.execute('SELECT DISTINCT(partner_id) FROM stock_reservation_product WHERE reservation_id = %s',(reservation.id,))
            for item in cr.fetchall():
                res.append(item[0])
            result[reservation.id] = res
        return result

    def _get_orders(self, cr, uid, ids, name, args, context=None):
        result = {}
        for reservation in self.browse(cr, uid, ids, context=context):
            res = []
            cr.execute('SELECT DISTINCT(order_id) FROM stock_reservation_product WHERE reservation_id = %s',(reservation.id,))
            for item in cr.fetchall():
                res.append(item[0])
            result[reservation.id] = res
        return result        
    
    _columns = {
                'name': fields.char('Number',select=True),
                                
                'state': fields.selection([('pre_init', 'New'),
                                           ('draft', 'Draft'),
                                           ('cancel', 'Cancelled'),
                                           ('confirmed', 'Confirmed'),
                                           ('done', 'Done'),
                                           ], 'State', readonly=True, select=True, copy=False),
                                
                'product_tmpl_id': fields.many2one('product.template','Template', readonly = True, required = True, states={'pre_init': [('readonly', False)]}),
                'color': fields.many2one('product.attribute.value','Color', required = True, readonly = True, states={'pre_init': [('readonly', False)]}),
                'user_id': fields.many2one('res.users','Author'),
                'location_id': fields.many2one('stock.location','Location', required = True, domain=[('usage','<>','view')], readonly = True, states={'pre_init': [('readonly', False)]}),
                'season_id': fields.many2one('res.family','Season', required = True, domain=[('type','=','production')], readonly = True, states={'pre_init': [('readonly', False)]}),
                
                'availability_line_ids': fields.one2many('stock.reservation.availability','reservation_id','Availabilities'),
                'reservation_product_ids': fields.one2many('stock.reservation.product','reservation_id','Reservations per Picking'),
                
                'date_from': fields.datetime('From', required = True, readonly = True, states={'pre_init': [('readonly', False)]}),
                'date_to': fields.datetime('To', required = True, readonly = True, states={'pre_init': [('readonly', False)]}),
                'date_confirmation': fields.datetime('Date Confirmation'),                

                'partner_ids': fields.function(_get_partners, string='Partners', relation="res.partner", method=True, type="many2many"),
                'order_ids': fields.function(_get_orders, string='Orders', relation="sale.order", method=True, type="many2many"),
                
                'order_id': fields.many2one('sale.order','Sale Order'), 
                'partner_id': fields.many2one('res.partner','Partner'),                
                'view_reservation_product_ids': fields.function(_get_res_lines, fnct_inv=_set_res_lines, string='Showed Reservations per Picking', relation="stock.reservation.product", method=True, type="one2many"),

    }

    def _get_location(self, cr, uid, context=None):
        cr.execute('''SELECT id FROM stock_location WHERE active = TRUE AND usage = 'internal' ORDER BY id ''')
        res = cr.fetchone()
        if res:
            return res
        return False

    def _get_season(self, cr, uid, context = None):
        seasons = self.pool.get('res.family').search(cr,uid,[('current','=',True)])
        if seasons:
            return seasons[0]
        return 
    
    def _get_user(self, cr, uid, context = None):
        return uid
    
    def _get_date_from(self, cr, uid, context = None):
        seasons = self.pool.get('res.family').search(cr,uid,[('current','=',True)])
        if seasons:
            return self.pool.get('res.family').browse(cr,uid,seasons[0]).date_start
        return     

    def _get_date_to(self, cr, uid, context = None):
        seasons = self.pool.get('res.family').search(cr,uid,[('current','=',True)])
        if seasons:
            return self.pool.get('res.family').browse(cr,uid,seasons[0]).date_end
        return     

    def _check_unicity(self, cr, uid, ids, context=None):
        this = self.browse(cr,uid,ids)
        if not this:
            return False
        res = self.search(cr, uid, [('product_tmpl_id','=',this.product_tmpl_id.id),('color','=',this.color.id),('location_id','=',this.location_id.id),('id','not in', ids),('state','in',['pre_init','draft'])])
        if res:
            return False        
        return True    

    def _update_availabilities(self, cr, uid, ids, on_create=False , context=None):
        for id in ids:
            availability_obj = self.pool.get('stock.reservation.availability')
            parent_obj = self.browse(cr, uid, id, context=context)
            
            product_ids = []
            tmp_product_ids = self.pool.get('product.template').browse(cr,uid,parent_obj.product_tmpl_id.id).product_variant_ids
            for product_id in tmp_product_ids:
                if parent_obj.color in product_id.attribute_value_ids:
                    product_ids.append(product_id.id)
            
            for product_id in product_ids:
                cr.execute('''
                    SELECT SUM (qty)
                    FROM stock_quant
                    WHERE
                        qty > 0 AND
                        reservation_id IS null AND
                        product_id = %s AND
                        location_id = %s
                ''',(product_id, parent_obj.location_id.id))
                quant_qty = cr.fetchone()
                if quant_qty and quant_qty[0]:
                    quant_qty = quant_qty[0]
                else:
                    quant_qty = 0.0

                cr.execute('''
                    SELECT SUM (qua.qty)
                    FROM stock_quant AS qua, stock_location AS loc
                    WHERE
                        qua.qty > 0 AND
                        qua.reservation_id IS null AND
                        qua.product_id = %s AND
                        qua.location_id != %s AND
                        qua.location_id = loc.id AND
                        loc.usage = 'internal'
                        
                ''',(product_id, parent_obj.location_id.id))
                external_qty = cr.fetchone()
                if external_qty and external_qty[0]:
                    external_qty = external_qty[0]
                else:
                    external_qty = 0.0

                cr.execute('''
                    SELECT SUM (qty)
                    FROM stock_quant
                    WHERE
                        qty > 0 AND
                        reservation_id IS NOT null AND
                        product_id = %s AND
                        location_id = %s
                ''',(product_id, parent_obj.location_id.id))
                ass_qty = cr.fetchone()
                if ass_qty and ass_qty[0]:
                    ass_qty = ass_qty[0]
                else:
                    ass_qty = 0.0
                
                cr.execute('''
                    SELECT SUM(mov.product_qty)
                    FROM 
                        stock_move AS mov,
                        procurement_order AS proc,
                        sale_order_line AS lin,
                        sale_order AS ord
                    WHERE
                        mov.procurement_id = proc.id AND
                        proc.sale_line_id = lin.id AND
                        lin.order_id = ord.id AND
                        ord.season = %s AND
                        ord.document_type_id IS null AND
                        ord.delivery_date BETWEEN %s AND %s AND
                        mov.state NOT IN ('cancel','done') AND
                        mov.product_id = %s  
                ''',(parent_obj.season_id.id, parent_obj.date_from, parent_obj.date_to, product_id))
                req_qty = cr.fetchone()
                if req_qty and req_qty[0]:
                    req_qty = req_qty[0]
                else:
                    req_qty = 0.0                
                
                if on_create:
                    availability_obj.create(cr,uid,{'reservation_id':id,'product_id':product_id, 'original_available_qty':quant_qty, 'available_qty':quant_qty, 'external_available_qty': external_qty, 'required_qty': req_qty, 'assigned_qty': ass_qty, 'original_assigned_qty': ass_qty, 'residual': quant_qty - req_qty})
                else:
                    cr.execute('''
                        SELECT SUM (rev.reserved_qty-rev.previously_reserved_qty)
                        FROM stock_reservation_product AS rev, stock_move AS mov
                        WHERE
                            rev.reservation_id = %s AND
                            rev.product_id = %s AND
                            rev.move_id = mov.id AND
                            mov.location_id = %s
                    ''',(ids[0], product_id, parent_obj.location_id.id))
                    reserved_qty = cr.fetchone() 
                    if reserved_qty and reserved_qty[0]:
                        reserved_qty = reserved_qty[0]
                    else:
                        reserved_qty = 0.0

                    cr.execute('''
                        SELECT SUM (rev.requested_qty)
                        FROM stock_reservation_product AS rev, stock_move AS mov
                        WHERE
                            rev.reservation_id = %s AND
                            rev.product_id = %s AND
                            rev.move_id = mov.id AND
                            mov.location_id = %s
                    ''',(ids[0], product_id, parent_obj.location_id.id))
                    requested_qty = cr.fetchone() 
                    if requested_qty and requested_qty[0]:
                        requested_qty = requested_qty[0]
                    else:
                        requested_qty = 0.0
                    
                    availability_line_id = availability_obj.search(cr, uid, [('reservation_id','=',id),('product_id','=',product_id)])
                    p_ass_qty = availability_obj.browse(cr, uid, availability_line_id, context=context).original_assigned_qty or 0
                    p_req_qty = availability_obj.browse(cr, uid, availability_line_id, context=context).required_qty  
                    availability_obj.write(cr, uid, availability_line_id,{'original_available_qty':quant_qty, 'available_qty':quant_qty-reserved_qty, 'external_available_qty': external_qty, 'assigned_qty':p_ass_qty+reserved_qty, 'required_qty': requested_qty, 'residual': quant_qty - requested_qty})                              
        return    

    def _auto_assign(self, cr, uid, ids, coherent=True, context=None):
        reservation_obj = self.pool.get('stock.reservation.product')
        availability_obj = self.pool.get('stock.reservation.availability')
        parent_obj = self.browse(cr, uid, ids[0], context=context)
        
        if coherent:
            for reservation in parent_obj.reservation_product_ids:
                reservation_obj.write(cr, uid, reservation.id, {'reserved_qty':reservation.previously_reserved_qty, 'difference':0.0})
            self._update_availabilities(cr,uid,ids)
        
        for availability in parent_obj.availability_line_ids:
            avl = availability.available_qty
            ass_qty = availability.assigned_qty
            orig_avl = availability.available_qty
            if coherent and avl == 0.0:
                continue
            for reservation in parent_obj.reservation_product_ids:
                if reservation.product_id == availability.product_id and not reservation.is_invisible:
                    if reservation.requested_qty - reservation.reserved_qty < avl or not coherent:
                        avl -= reservation.requested_qty - reservation.reserved_qty                        
                        reservation_obj.write(cr,uid,reservation.id,{'reserved_qty':reservation.requested_qty, 'difference':reservation.requested_qty - reservation.previously_reserved_qty})
                    elif coherent:
                        reservation_obj.write(cr,uid,reservation.id,{'reserved_qty':reservation.reserved_qty+avl, 'difference':reservation.difference+avl})
                        avl = 0.0
                    if coherent and avl == 0.0:
                        break
            availability_obj.write(cr,uid,availability.id,{'available_qty':avl, 'assigned_qty': ass_qty + orig_avl - avl })
        return
    
    def _reserve_quants(self, cr, uid, ids, context=None):
        context = context or {}
        quant_obj = self.pool.get("stock.quant")
        move_obj = self.pool.get('stock.move')
        reservation_obj = self.pool.get('stock.reservation.product')
        availability_obj = self.pool.get('stock.reservation.availability')
        parent_obj = self.browse(cr, uid, ids[0], context=context)        
        
        for line in parent_obj.reservation_product_ids:
            '''
            if line.location_id != parent_obj.location_id:
                continue
            '''
            mov_obj = self.pool.get('stock.move')              
            if line.difference == 0:
                continue
            if line.difference < 0:
                move_obj.do_unreserve(cr, uid, line.move_id.id,context=context)
                qty_already_assigned = 0.0
            else:
                qty_already_assigned = line.move_id.reserved_availability
            
            main_domain = [('reservation_id', '=', False), ('qty', '>', 0)]

            qty = line.reserved_qty - qty_already_assigned
            if qty > 0:
                quants = quant_obj.quants_get_prefered_domain(cr, uid, parent_obj.location_id, line.product_id, qty, domain=main_domain, context=context)
                quant_obj.quants_reserve(cr, uid, quants, line.move_id, context=context)     
                   
                if line.location_id == parent_obj.location_id:
                    continue
                pick_id = self.pool.get('stock.picking.type').search(cr, uid, [('code','=','outgoing'),('default_location_src_id','=',parent_obj.location_id.id)], context=context)
                mov_obj.write(cr, uid, line.move_id.id, {'location_id': parent_obj.location_id.id,'picking_type_id': pick_id[0]}, context=context)
        return 

    _defaults = {
        'user_id': _get_user,
        'season_id': _get_season,
        'location_id': _get_location,
        'date_from': _get_date_from,
        'date_to': _get_date_to,
        'state': 'pre_init',
    }    

    _constraints = [(_check_unicity, "You already are planning the delivery of these products.",['product_tmpl_id','color','location_id']),]

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def button_clear_filter(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'partner_id':None,'order_id':None},context=context)

    def onchange_template_id(self, cr, uid, ids, template_id):
        ids = []
        if template_id:
            tmpl_obj = self.pool.get('product.template').browse(cr, uid, template_id)
            if tmpl_obj and tmpl_obj.attribute_line_ids:
                for line in tmpl_obj.attribute_line_ids:
                    if line.attribute_id.position == 'row':
                        for id in line.value_ids.ids:
                            ids.append(id)

        return {'domain': {'color':[('id','in',ids)]}}

    def onchange_season_id(self, cr, uid, ids, season_id):
        res = {'value':{}}
        if season_id:
            res['value'].update({'date_to':self.pool.get('res.family').browse(cr,uid,season_id).date_end})
            res['value'].update({'date_from':self.pool.get('res.family').browse(cr,uid,season_id).date_start})
        return res            

    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        for reservation in self.browse(cr, uid, ids, context=context):
            if reservation.state not in ('pre_init', 'draft', 'cancel'):
                raise osv.except_osv(_('User Error!'), _('You cannot delete confirmed items.'))
        return super(stock_template_reservation, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(stock_template_reservation, self).write(cr, uid, ids, vals, context=context)
        if 'reservation_product_ids' in vals:
            for id in ids:
                res_obj = self.browse(cr,uid,id)
                for avl_line in res_obj.availability_line_ids:
                    diff = 0.0
                    cr.execute('''
                        SELECT SUM(difference)
                        FROM stock_reservation_product
                        WHERE 
                            reservation_id = %s AND
                            product_id = %s
                    ''',(id, avl_line.product_id.id))
                    tmp = cr.fetchone()
                    if tmp and tmp[0]:
                        diff = tmp[0]
                    self.pool.get('stock.reservation.availability').write(cr,uid,avl_line.id,{'available_qty':avl_line.original_available_qty - diff, 'assigned_qty':avl_line.original_assigned_qty + diff})
        return res   
    
    def create_reservation_lines(self, cr, uid, ids, context=None):
        for id in ids:
            reservation_obj = self.pool.get('stock.reservation.product')
            parent_obj = self.browse(cr, uid, id, context=context)
            
            product_ids = []
            for line in parent_obj.availability_line_ids:
                product_ids.append(line.product_id.id)
            
            for product_id in product_ids:     
                cr.execute('''
                    SELECT mov.id
                    FROM 
                        stock_move AS mov,
                        procurement_order AS proc,
                        sale_order_line AS lin,
                        sale_order AS ord
                    WHERE
                        mov.procurement_id = proc.id AND
                        proc.sale_line_id = lin.id AND
                        lin.order_id = ord.id AND
                        ord.season = %s AND
                        ord.document_type_id IS null AND
                        ord.delivery_date BETWEEN %s AND %s AND
                        mov.state NOT IN ('cancel','done') AND
                        
                        mov.product_id = %s            
                ''',(parent_obj.season_id.id, parent_obj.date_from, parent_obj.date_to,  product_id))
                move_ids = cr.fetchall()
                for move_id in move_ids:
                    pre = self.pool.get('stock.move').browse(cr,uid,move_id[0]).reserved_availability
                    reservation_obj.create(cr,uid,{'reservation_id':id,'move_id':move_id[0],'difference':0.0,'reserved_qty':pre,'previously_reserved_qty':pre})                
        return
    
    def action_recheck(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        return self._update_availabilities(cr, uid, ids)
        
    def action_auto_assign(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'       
        return self._auto_assign(cr, uid, ids, True, context)
    
    def action_reserve_all(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'       
        return self._auto_assign(cr, uid, ids, False, context)    
       
    def action_start(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'reservation_start')
        return True    

    def action_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        for line in self.browse(cr,uid,ids[0]).availability_line_ids:
            if line.available_qty < 0.0:
                raise osv.except_osv(_('Error!'), _('You are trying to reserve more product than you have in this location.'))
        self.signal_workflow(cr, uid, ids, 'reservation_confirm')
        return True        
    
    def action_close(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'reservation_close')
        return True    
    
    def action_cancel(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.signal_workflow(cr, uid, ids, 'reservation_cancel')
        return True            
  
    def start_reservation(self, cr, uid, ids, context=None):
        self._update_availabilities(cr, uid, ids, True, context=context)
        self.create_reservation_lines(cr, uid, ids, context=context)
        #    GENERAZIONE RIGHE DI EVASIONE
        self.write(cr,uid,ids,{'state':'draft'})
        return True

    def confirm_reservation(self, cr, uid, ids, context=None):
        self._reserve_quants(cr, uid, ids, context=context)      
        name = self.pool.get('ir.sequence').get(cr, uid, 'stock.template.reservation')
        date_now = datetime.now().strftime('%Y-%m-%d')        
        self.write(cr,uid,ids,{'state':'confirmed', 'name':name, 'date_confirmation': date_now}, context=context)
        return True    
    
