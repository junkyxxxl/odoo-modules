# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
#    Copyright (C) 2015
#    Andrea Cometa <a.cometa@apuliasoftware.it>
#    WEB (<http://www.apuliasoftware.it>).
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging


_logger = logging.getLogger(__name__)


class ProductionAnalysis(models.TransientModel):
    """Production analysis"""
    _name = "sale.analysis.production"
    # filters
    user_id = fields.Many2one(
        'res.users', string="Analysis User",
        default=lambda self: self.env.user)
    date_begin = fields.Date(
        string="Start Date", default=fields.Datetime.now())
    date_end = fields.Date(
        string="End Date", default=fields.Datetime.now())
    quotations = fields.Boolean(string="Quotation")
    orders = fields.Boolean(string="Orders")
    print_result = fields.Boolean(string="Print Result")
    category_ids = fields.Many2many('product.category',
                                    string="Product Categoy")
    family_ids = fields.Many2many('res.family',
                                  string="Product Family")
    recursive = fields.Boolean(string="Recursive", default=False)
    season = fields.Many2one('res.family',
                             domain="[('type','=','production')]")
    document_type = fields.Many2one('sale.document.type', string="Tipo Documento")
    all_document_type = fields.Boolean(string="Tutti")
    order_ids = fields.Many2many('sale.order')

    partner_ids = fields.Many2many('res.partner')
    f_delivery_date = fields.Date(string='From Delivery Date')
    t_delivery_date = fields.Date(string='To Delivery Date')
    exclude_shipped = fields.Boolean(string='Exclude Shipped Order',
                                     default=False)
    template_ids = fields.Many2many(
        'product.template', string="Parent Product")
    # custom filters

    @api.multi
    def clear_data(self):
        analysis_obj = self.env['sale.analysis']
        analysis_type = 'sale'
        if str(self._model) == 'purchase.analysis.production':
            analysis_type = 'purchase'
        record_ids = analysis_obj.search(
            [('user_id', '=', self.env.user.id),
             ('analysis_type', '=', analysis_type)])
        if record_ids:
            record_ids.unlink()
        return True

    def compute_lines(self, analysis_dict={}, product_id=None, qty=0.0,
                      recursive=False, order_id=False, master_bom_id=False,
                      line_type=''):
        product_obj = self.env['product.product']
        bom_model = self.env['mrp.bom']
        bom_id = bom_model._bom_find(
            None, product_id.id)
        if bom_id:
            if not master_bom_id:
                master_bom_id = bom_id
            bom = bom_model.browse(bom_id)
            res = bom_model._bom_explode(
                bom, product_id, qty)
            #    # process bom
            for bom_line in res[0]:
                # write components only 1 time for user:
                product = product_obj.browse(
                    bom_line['product_id'])
                # check if product is bom and if recursion yes
                bom2_id = bom_model._bom_find(None, product.id)
                if recursive and bom2_id:
                    analysis_dict = self.compute_lines(
                        analysis_dict, product, bom_line['product_qty'],
                        recursive, False, master_bom_id, line_type)
                else:
                    if not master_bom_id in analysis_dict:
                        analysis_dict.update({master_bom_id: {}})  

                    if product.id in analysis_dict[master_bom_id]:
                        analysis_dict[master_bom_id][product.id][
                            'qty'] += bom_line['product_qty']
                        _logger.info('Dict aggiornato: %s' % (product.name))
                    else:
                        analysis_dict[master_bom_id].update({product.id: {
                            'name': '',
                            'bom_id': master_bom_id,
                            'uom': bom_line['product_uom'],
                            'qty': bom_line['product_qty'],
                            'order_id': order_id,
                            'type': line_type,
                            'qty_available': product.qty_available,
                            'order_qty': product.incoming_qty,
                        }})
                        _logger.info('Articolo Aggiunto: %s' % (product.name))
        _logger.info('Chiavi Dict: %s' % len(analysis_dict.keys()))
        return analysis_dict

    @api.multi
    def confirm(self):
        analysis_obj = self.env['sale.analysis']
        product_obj = self.env['product.product']
        #  Unlink old data for the same user_id
        self.clear_data()
        if (not self.quotations and not self.orders) and not self.order_ids:

            if not str(self._model) == 'purchase.analysis.production':
                raise Warning(_(
                    'At least one of "quotations" and "orders" '
                    'must be selected'))
        states = []
        if self.quotations:
            states.append('draft')
            states.append('sent')
        if self.orders:
            states.append('waiting_date')
            states.append('progress')
            states.append('manual')
        if str(self._model) == 'purchase.analysis.production':
            states = []
            if self.quotations:
                states = ('draft', 'sent')
            if self.orders:
                 states = ('confirmed', 'approved',
                           'except_picking', 'except_invoice', 'done')
        args = [
            ('date_order', '>=', self.date_begin),
            ('date_order', '<=', self.date_end),  ]
        if states:
            args.append(('state', 'in', states))
        # add here others fields
        if self.season and str(self._model) == 'sale.analysis.production':
            args.append(('season', '=', self.season.id))
        if not self.all_document_type and str(self._model) == 'sale.analysis.production':
            if self.document_type: 
                args.append(('document_type_id', '=', self.document_type.id))            
            else:
                args.append(('document_type_id', 'in', [False,None]))
        if self.partner_ids:
            args.append(
                ('partner_id', 'in', tuple([p.id for p in self.partner_ids])))
        if self.t_delivery_date and self.f_delivery_date:
            args.append(('delivery_date', '<=', self.t_delivery_date))
            args.append(('delivery_date', '>=', self.f_delivery_date))
        orders = self.env['sale.order'].search(args)
        if str(self._model) == 'purchase.analysis.production':
            orders = self.env['purchase.order'].search(args)
        if self.order_ids:
            # order_ids = [o.id for o in ]
            orders = self.order_ids
        if str(self._model) == 'purchase.analysis.production' and \
                self.purchase_ids:
            orders = self.purchase_ids
        # get product category
        categ_ids = []
        if self.category_ids:
            for categ in self.category_ids:
                categ_ids.append(self.env['product.category'].category_map(
                    categ, categ_ids
                ))

        family_ids = []
        if self.family_ids:
            family_ids = [f.id for f in self.family_ids]

        parent_ids = []
        if self.template_ids:
            parent_ids = [p.id for p in self.template_ids]


        analysis_dict = {}
        for order in orders:
            # build array of products with manufacture type and sum quantities
            if self.exclude_shipped and order.shipped:
                continue
            line_type = 'Order'
            if order.state in ('draft', 'sent'):
                line_type = 'Quotations'
            if str(self._model) == 'purchase.analysis.production':
                line_type = 'Purchase'
            for line in order.order_line:
                if categ_ids and line.product_id.categ_id.id not in categ_ids:
                    continue
                if family_ids and not line.product_id.famiglia:
                    continue
                if family_ids and line.product_id.famiglia.id not in family_ids:
                    continue
                template_id = line.product_id.product_tmpl_id.id
                if parent_ids and template_id not in parent_ids:
                    continue
                for route in line.product_id.route_ids:
                    if route.name == 'Manufacture':
                        if str(self._model) == 'sale.analysis.production':
                            qty = line.product_uom_qty
                        if str(self._model) == 'purchase.analysis.production':
                            qty = line.product_qty
                        analysis_dict = self.compute_lines(
                            analysis_dict, line.product_id,
                            qty, self.recursive, order.id, False, line_type)

        # now create the record
        if analysis_dict:
            analysis_type = 'sale'
            if str(self._model) == 'purchase.analysis.production':
                analysis_type = 'purchase'
            analysis_obj = self.env['sale.analysis']
            for bom in analysis_dict:
                for product in analysis_dict[bom]:

                    vals = analysis_dict[bom][product].copy()
                    vals.update({
                        'user_id': self.env.user.id,
                        'residual': vals['qty_available'] - vals['qty'],
                        'product_id': product,
                        'date_begin': self.date_begin,
                        'date_end': self.date_end,
                        'analysis_type': analysis_type,
                    })
                    if str(self._model) == 'purchase.analysis.production':
                        del vals['order_id']
                    analysis_obj.create(vals)

        if self.print_result:
            report = 'isa_sale_analisys.summary_requirement_qweb'
            data = {'lines': []}
            return self.env['report'].get_action(self, report, data=data)

        # open the view
        ir_model_data = self.env['ir.model.data']
        try:
            view_id = ir_model_data.get_object_reference(
                'isa_sale_analisys', 'sale_analysis_tree')[1]
        except ValueError:
            view_id = False
        res = {
            'name': _('Analysis Line'),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sale.analysis',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'context': {'search_default_user_id': self.env.user.id},
            'domain': [('analysis_type', '=', 'sale')],
        }
        if str(self._model) == 'purchase.analysis.production':
            res['domain'] = [('analysis_type', '=', 'purchase')]
        return res