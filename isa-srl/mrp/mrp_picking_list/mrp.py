# -*- coding: utf-8 -*-

from openerp import api, models, fields
from openerp.osv import orm
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.tools import float_compare, float_is_zero
from openerp.exceptions import Warning



class mrp_production(models.Model):

    _inherit = "mrp.production"

    @api.multi
    def _compute_performance(self):
        produced_lines = self.move_created_ids2
        produced_qty = 0
        for produced_line in produced_lines:
            produced_qty += produced_line.product_uom_qty
        self.mrp_performance = (produced_qty/self.product_qty)*100

    @api.multi
    def _src_id_default(self):
        try:
            location_id = self.env.user.company_id.location_src_id.id
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id

    @api.multi
    def _tmp_id_default(self):
        try:
            location_id = self.env.user.company_id.location_tmp_id.id
        except (orm.except_orm, ValueError):
            location_id = False
        return location_id
        
    location_tmp_id = fields.Many2one('stock.location', 'Ubicazione materie prime',required=True, readonly=True, states={'draft': [('readonly', False)]},
        help="Location where the system will stock the products required for production")
    distinct_picking_id = fields.Many2one('stock.picking', 'Distinta Prelievo',readonly=True,
        help="Picking linked to mrp production order")
    state = fields.Selection(string='Status', readonly=True, selection=[('draft', 'New'), ('cancel', 'Cancelled'),
                ('confirmed', 'Awaiting Raw Materials'),
                ('ready', 'Ready to Produce'), ('in_production', 'Production Started'), ('scrap_op', 'Scrap Management'), ('done', 'Done')])
    move_lines = fields.One2many('stock.move', 'raw_material_production_id', 'Products to Consume',
            domain=[('state', 'not in', ('done', 'cancel'))],readonly=False)

    mrp_performance = fields.Float(string = 'Resa Produzione', digits=dp.get_precision('Account'), compute='_compute_performance')

    _defaults = {
        'location_src_id': _tmp_id_default,
        'location_tmp_id': _src_id_default
    }    

    @api.model
    def _calculate_qty(self, production, product_qty=0.0):
        """
            Calculates the quantity still needed to produce an extra number of products
            product_qty is in the uom of the product
        """
        quant_obj = self.pool.get("stock.quant")
        uom_obj = self.pool.get("product.uom")
        produced_qty = self._get_produced_qty(production)
        consumed_data = self._get_consumed_data(production)

        # In case no product_qty is given, take the remaining qty to produce for the given production
        if not product_qty:
            product_qty = uom_obj._compute_qty(self._cr, self._uid, production.product_uom.id, production.product_qty,
                                               production.product_id.uom_id.id) - produced_qty
        production_qty = uom_obj._compute_qty(self._cr, self._uid, production.product_uom.id, production.product_qty,
                                              production.product_id.uom_id.id)

        scheduled_qty = OrderedDict()
        for scheduled in production.product_lines:
            if scheduled.product_id.type == 'service':
                continue
            qty = uom_obj._compute_qty(self._cr, self._uid, scheduled.product_uom.id, scheduled.product_qty,
                                       scheduled.product_id.uom_id.id)
            if scheduled_qty.get(scheduled.product_id.id):
                scheduled_qty[scheduled.product_id.id] += qty
            else:
                scheduled_qty[scheduled.product_id.id] = qty
        dicts = OrderedDict()
        # Find product qty to be consumed and consume it
        for product_id in scheduled_qty.keys():

            consumed_qty = consumed_data.get(product_id, 0.0)

            # qty available for consume and produce
            sched_product_qty = scheduled_qty[product_id]
            qty_avail = sched_product_qty - consumed_qty
            if qty_avail <= 0.0:
                # there will be nothing to consume for this raw material
                continue

            if not dicts.get(product_id):
                dicts[product_id] = {}

            # total qty of consumed product we need after this consumption
            # forzo il ricalcolo anche se la quantità prodotta è maggiore di quella iniziale

            #if product_qty + produced_qty <= production_qty:
            total_consume = ((product_qty + produced_qty) * sched_product_qty / production_qty)
            #else:
            #    total_consume = sched_product_qty
            qty = total_consume - consumed_qty

            # Search for quants related to this related move
            for move in production.move_lines:
                if qty <= 0.0:
                    break
                if move.product_id.id != product_id:
                    continue

                q = min(move.product_qty, qty)
                quants = quant_obj.quants_get_prefered_domain(self._cr, self._uid, move.location_id, move.product_id, q,
                                                              domain=[('qty', '>', 0.0)],
                                                              prefered_domain_list=[[('reservation_id', '=', move.id)]],
                                                              )
                for quant, quant_qty in quants:
                    if quant:
                        lot_id = quant.lot_id.id
                        if not product_id in dicts.keys():
                            dicts[product_id] = {lot_id: quant_qty}
                        elif lot_id in dicts[product_id].keys():
                            dicts[product_id][lot_id] += quant_qty
                        else:
                            dicts[product_id][lot_id] = quant_qty
                        qty -= quant_qty
            if float_compare(qty, 0,
                             self.pool['decimal.precision'].precision_get(self._cr, self._uid, 'Product Unit of Measure')) == 1:
                if dicts[product_id].get(False):
                    dicts[product_id][False] += qty
                else:
                    dicts[product_id][False] = qty

        consume_lines = []
        for prod in dicts.keys():
            for lot, qty in dicts[prod].items():
                consume_lines.append({'product_id': prod, 'product_qty': qty, 'lot_id': lot})
        return consume_lines

     #Genero un picking dal mazazzino principale al magazzino temporaneo
    @api.multi
    def action_transfer_to_tmp_stock(self):
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Movimentazione Magazzino Temporaneo')])
        stock_picking_obj = self.env['stock.picking']
        picking_lines = []
        for move_line in self.move_lines:
            picking_line = {
                        'product_id': move_line.product_id.id,
                        'product_uom_qty': move_line.product_uom_qty,
                        'product_uom': move_line.product_uom.id,
                        'location_id': self.location_tmp_id.id,
                        'location_dest_id': self.location_src_id.id,
                        'invoice_state': 'none',
                        'name': move_line.product_id.name,
                   }
            picking_lines.append((0, 0, picking_line))

        vals = {
            'partner_id': self.user_id.company_id.partner_id.id,
            'origin': self.name,
            'move_type': 'direct',
            'invoice_state': 'none',
            'picking_type_id': picking_type_id.id,
            'move_lines': picking_lines,
            'name': 'Distinta Ordine %s' %self.name
        }
        picking_obj = stock_picking_obj.create(vals)
        self.pool.get("stock.picking").action_confirm(self._cr, self._uid, picking_obj.id, self._context)

        self.pool.get("stock.picking").action_assign(self._cr, self._uid, picking_obj.id, self._context)
        self.distinct_picking_id = picking_obj.id
        return {
                "type": "ir.actions.act_window",
                "res_model": "stock.picking",
                "views": [[False, "form"]],
                "res_id":  picking_obj.id,
            }

    @api.model
    def action_produce(self,production_id, production_qty, production_mode, wiz=False):
        mrp_prod_obj = self.env['mrp.production'].browse(production_id)
        #check total quantity for production line


        if wiz:
            for consume_line in wiz.consume_lines:
                sql = ''' SELECT
                                SUM(qty) as total_qty
                            FROM
                                stock_quant
                            WHERE
                                location_id = %s AND
                                product_id =  %s
                            GROUP BY
                                product_id'''

                self.env.cr.execute(sql, (mrp_prod_obj.location_src_id.id, consume_line.product_id.id,))
                queryResult = self.env.cr.fetchall()
                if consume_line.product_qty > queryResult[0][0]:
                    raise Warning('Quantita nel magazzino temporaneo per il prodotto\n %s \nnon sufficiente per la produzione richiesta.\n(Quantita richiesta: %d Quantità disponibile: %d)' %(str(consume_line.product_id.name),consume_line.product_qty,queryResult[0][0]))

        super(mrp_production,self).action_produce(production_id, production_qty, production_mode, wiz)
        #svuoto i pacchi del magazzino temporaneo
        for move in mrp_prod_obj.distinct_picking_id.move_lines:
            for quant in move.quant_ids:
                quant.package_id = None
        mrp_prod_obj.signal_workflow('scrap_on')
        return True

    @api.multi
    def return_stock_mrp(self):
        context =   {'default_mrp_order_id' : self.id,
                     'default_state' : self.state,
                     'product_ids' : 20,
                     }
        return {
                "type": "ir.actions.act_window",
                "res_model": "return.stock.mrp",
                "views": [[False, "form"]],
                "target": "new",
                "context": context
            }
