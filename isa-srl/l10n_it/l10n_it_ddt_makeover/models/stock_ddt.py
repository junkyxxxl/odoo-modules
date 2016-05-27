# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Abstract (http://www.abstract.it)
#    @author Davide Corio <davide.corio@abstract.it>
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api, tools
from openerp.exceptions import except_orm
from openerp.tools.translate import _
import time
import pytz
from openerp import SUPERUSER_ID 
import datetime

class StockDdT(models.Model):

    _inherit = 'stock.ddt'

    
    #imposta l'ora di creazione del ddt sempre a 00:00:00 indipendentemente dal timezone
    def _getDefaultDate(self):
        src_tstamp_str = tools.datetime.now().strftime('%Y-%m-%d')
        dst_format = "%Y-%m-%d %H:%M:%S" #format you want to get time in. 
        dst_tz_name =  self.env.user.tz
        to_date_time = (datetime.datetime.combine(datetime.datetime.now(), datetime.time(0, 0)))

        return to_date_time

    def _get_company_default(self):
        if self.partner_id and self.partner_id.company_id:
            return self.partner_id.company_id
        return self.env['res.users'].browse(self._uid).company_id

    weight = fields.Float(string='Peso', copy=False)
    weight_net = fields.Float(string='Peso Netto', copy=False)

    date_done = fields.Date(string='Data consegna')

    carrier_id = fields.Many2one('delivery.carrier', string='Carrier')
    
    company_id = fields.Many2one('res.company', string='Company', default=_get_company_default)

    incoterm_id = fields.Many2one('stock.incoterms',
                                  string='Condizione di Consegna (Incoterm)',
                                  help="International Commercial Terms are a series of predefined commercial terms used in international transactions."
                                  )

    user_id = fields.Many2one('res.users', string='Commerciale')

    payment_term = fields.Many2one('account.payment.term', string='Termine di Pagamento')

    invoice_id = fields.Many2one('account.invoice', string='Fattura')

    to_be_invoiced = fields.Boolean(string='Da Fatturare', compute='_get_to_be_invoiced', store=True)

    picking_ids_return = fields.One2many('stock.picking', 'ddt_id', string='Returned Pickings', readonly=True, compute='_get_pickings_return')
    
    ddt_lines_return = fields.One2many('stock.move', 'ddt_id', string='Returned DdT Line', readonly=True, compute='_get_lines_return')

    total_value = fields.Float(string='Imponibile Totale', compute='_get_total_value', store=False, copy=False)

    note2 = fields.Text('Note')
    
    ddt_date = fields.Date('Data DDT', required=False, store=True, compute='_compute_ddt_date')
    
    date = fields.Datetime(required=True, default=_getDefaultDate)    

    @api.depends('date')
    def _compute_ddt_date(self):
        for record in self:
            if not record.date:
                return
            date_obj = datetime.datetime.strptime(self.date, '%Y-%m-%d %H:%M:%S')
            record.ddt_date = date_obj.date()

    @api.multi
    #@api.depends('picking_ids', 'picking_ids.state')
    def _get_total_value(self):
        for ddt in self:
            tot = 0.0
            for ddt_line in ddt.ddt_lines:
                if ddt_line.procurement_id and ddt_line.procurement_id.sale_line_id:
                    line = ddt_line.procurement_id.sale_line_id
                    tot += line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)  
                elif ddt_line.procurement_id and ddt_line.procurement_id.purchase_line_id:
                    line = ddt_line.procurement_id.purchase_line_id
                    tot += line.price_subtotal * (ddt_line.product_uom_qty / line.product_qty)
                elif ddt_line.purchase_line_id:
                    line = ddt_line.purchase_line_id
                    tot += line.price_subtotal * (ddt_line.product_uom_qty / line.product_qty)               
                                                             
            for ddt_line in ddt.ddt_lines_return:
                if ddt_line.procurement_id and ddt_line.procurement_id.sale_line_id:
                    line = ddt_line.procurement_id.sale_line_id
                    tot -= line.price_subtotal * (ddt_line.product_uom_qty / line.product_uom_qty)     
                elif ddt_line.procurement_id and ddt_line.procurement_id.purchase_line_id:
                    line = ddt_line.procurement_id.purchase_line_id
                    tot -= line.price_subtotal * (ddt_line.product_uom_qty / line.product_qty)
                elif ddt_line.purchase_line_id:
                    line = ddt_line.purchase_line_id
                    tot -= line.price_subtotal * (ddt_line.product_uom_qty / line.product_qty)                                                     
            ddt.total_value = tot

    @api.multi
    @api.depends('picking_ids', 'picking_ids.invoice_state')
    def _get_to_be_invoiced(self):
        for ddt in self:
            ddt.to_be_invoiced = False
            for picking in ddt.picking_ids:
                if picking.invoice_state == '2binvoiced':
                    ddt.to_be_invoiced = True
                    break

    @api.multi
    def _get_pickings_return(self):

        for ddt in self:
            for picking in ddt.picking_ids:
                back_ids = self.pool.get('stock.picking').search(self._cr, self._uid, [('origin','=',picking.name)], context=self._context)
                if back_ids:
                    ddt.picking_ids_return |= self.pool.get('stock.picking').browse(self._cr, self._uid, back_ids)
        
        for ddt in self:
            for picking in ddt.picking_ids_return:
                ddt.ddt_lines_return |= picking.move_lines

    @api.multi
    def _get_lines_return(self):
        for ddt in self:
            for picking in ddt.picking_ids:
                ddt.ddt_lines |= picking.move_lines

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.delivery_address_id = None

    @api.multi
    def set_number(self):
        for ddt in self:
            if not ddt.name:
                for pick in ddt.picking_ids:
                    if pick.picking_type_id.ddt_sequence_id:
                        ddt_number = self.pool.get('ir.sequence').next_by_id(self._cr, self._uid, pick.picking_type_id.ddt_sequence_id.id)
                        if ddt_number: 
                            ddt.name = ddt_number
                            break

    @api.multi
    def action_confirm(self):
        for ddt in self:
            if not ddt.ddt_lines:
                raise except_orm(_('Errore!'),_('Non puoi confermare un DDT senza righe!'))
            self.write({'state': 'confirmed','delivery_date': time.strftime('%Y-%m-%dT%H:%M:%S')})
        

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update(name=None)
        return super(StockDdT, self).copy(default)

    def view_partner_pickings(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        t_partner_list = []

        for ddt_data in self.browse(cr, uid, ids, context):
            if ddt_data.partner_id:
                t_partner_list.append(ddt_data.partner_id.id)

        if t_partner_list:
            mod_obj = self.pool.get('ir.model.data')
            result = mod_obj.get_object_reference(cr, uid,
                                                  'l10n_it_ddt_makeover',
                                                  'view_picking_makeover_form')
            view_id = result and result[1] or False

            return {'domain': "[('picking_type_id.code','=','outgoing'),('invoice_state','in', ['2binvoiced','none']),('ddt_id','not in', ["+','.join(map(str,ids))+"]),('partner_id','in', ["+','.join(map(str,t_partner_list))+"]),'|',('ddt_id','=', None),('ddt_id','=', False)]",
                    'name': _("Picking del Cliente"),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'context': context,
                    'views': [(False,'tree'),(view_id,'form')],
                    }
        return True
    
    @api.multi
    def write(self, values):
        '''
        if 'ddt_date' in values and values['ddt_date']:
            values.update({'date': values.get('ddt_date')})
        '''
        return  super(StockDdT, self).write(values)
    
    @api.model
    def create(self, values):
        return  super(StockDdT, self).create(values)    
