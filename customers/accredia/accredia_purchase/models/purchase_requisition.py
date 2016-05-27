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


class purchase_requisition(orm.Model):
    _inherit = 'purchase.requisition'

    _track = {
        'state': {
            'accredia_purchase.purchase_requisition_new': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft'],
        },
    }

    def create(self, cr, user, vals, context=None):

        if 'user_id' in vals and vals['user_id']:
            user_obj = self.pool.get('res.users')

            user_data = user_obj.browse(cr, user, vals['user_id'])
            t_partner_id = None
            if user_data.partner_id:
                t_partner_id = user_data.partner_id.id

            if t_partner_id:
                vals['message_follower_ids'] = [(4, t_partner_id)]

        res = super(purchase_requisition, self).create(cr, user, vals, context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]

        if 'user_id' in vals and vals['user_id']:
            user_obj = self.pool.get('res.users')

            user_data = user_obj.browse(cr, uid, vals['user_id'])
            t_partner_id = None
            if user_data.partner_id:
                t_partner_id = user_data.partner_id.id

            if t_partner_id:
                vals['message_follower_ids'] = [(4, t_partner_id)]

        res = super(purchase_requisition, self).write(cr,
                                                      uid,
                                                      ids,
                                                      vals,
                                                      context)
        return res

    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Supplier should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                raise orm.except_orm(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
            location_id = requisition.warehouse_id.lot_input_id.id
            purchase_id = purchase_order.create(cr, uid, {
                'origin': requisition.name,
                'partner_id': supplier.id,
                'pricelist_id': supplier_pricelist.id,
                'location_id': location_id,
                'company_id': requisition.company_id.id,
                'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                'requisition_id': requisition.id,
                'notes': requisition.description,
                'warehouse_id': requisition.warehouse_id.id,
                'department_id': requisition.department_id and requisition.department_id.id or None,
                'payment_term_id': supplier.property_supplier_payment_term and supplier.property_supplier_payment_term.id or None,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                product = line.product_id
                if not product:
                    raise orm.except_orm(_('Attenzione!'), _('Il Prodotto è obbligatorio per ciascuna riga di richiesta preventivo.'))
                seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
                taxes_ids = product.supplier_taxes_id
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                t_short_description = line.short_description or ''
                t_detailed_description = line.detailed_description or ''
                t_separator = t_short_description and t_detailed_description and ' ' or ''
                t_name = t_short_description + t_separator + t_detailed_description
                purchase_order_line.create(cr, uid, {
                    'order_id': purchase_id,
                    'name': t_name or product.partner_ref,
                    'product_qty': qty,
                    'product_id': product.id,
                    'product_uom': default_uom_po_id,
                    'price_unit': seller_price,
                    'date_planned': date_planned,
                    'taxes_id': [(6, 0, taxes)],
                }, context=context)

        return res

    _columns = {'object': fields.text('Object',
                                      translate=True),
                'reason': fields.text('Reason',
                                      translate=True),
                'project_id': fields.many2one('project.project',
                                              'Project'),
                'department_id': fields.many2one('hr.department',
                                                 'Department'),
                'requester_office_id': fields.many2one('doclite.uffici',
                                                       'Requester Office'),
                'task_id': fields.many2one('project.task',
                                           'Riferimento'),
                }
