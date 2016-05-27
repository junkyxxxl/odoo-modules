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

from openerp.osv import fields, orm, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_picking_discount(orm.Model):
    _inherit = 'stock.picking'

    def action_invoice_create(self, cr, uid, ids, journal_id, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        partner_discount = {}        
        if group:
            
            #Raggruppa i picking per partner
            for picking in self.browse(cr, uid, ids, context=context):  
                partner = self._get_partner_to_invoice(cr, uid, picking, context)
                if partner not in partner_discount:
                    partner_discount.setdefault(partner, [])
                partner_discount[partner].append(picking.sale_id)
            
            #Per ogni raggruppamento
            for entry_index in partner_discount:
                entry = partner_discount[entry_index]
                #Se il raggruppamento è di un solo elemento, o vuoto, non c'è bisogno di fare controlli ulteriori
                if len(entry)<=1:
                    continue

                '''Per ogni ordine di vendita del raggruppamento, confronta ad una ad una tutte le sue righe 
                   di sconto globale, che devono essere tutte uguali tra loro e dunque per definizione tutte
                   uguali alla prima'''                
                default = entry[0].global_discount_lines.sorted()                
                for sale in entry:
                    current = sale.global_discount_lines
                    if len(current) != len(default):
                        raise osv.except_osv(_('Discount Mismatch!'), _('It\'s not possible to group pickings that refers to sale orders with different global discounts.'))
                    for i in range(0,len(default)):
                        if (current[i].name != default[i].name) or (current[i].value != default[i].value) or (current[i].type != default[i].type):
                            raise osv.except_osv(_('Discount Mismatch!'), _('It\'s not possible to group pickings that refers to sale orders with different global discounts.'))
                                                                
        invoices = super(stock_picking_discount,self).action_invoice_create(cr, uid, ids, journal_id, group, type, context=context)
        return invoices
        
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal_id, move, context=None):
        inv_vals = super(stock_picking_discount, self)._get_invoice_vals(cr, uid, key, inv_type, journal_id, move, context=context)
        discount_line = []
        discount_line_ids = []
        if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id:
            discount_line = move.procurement_id.sale_line_id.order_id.global_discount_lines

            for line in discount_line:
                discount_line_ids.append(self.pool.get('account.invoice.discount').create(cr,uid,{'name':line.name.id,'type':line.type, 'application':line.application, 'sequence':line.sequence,'value':line.value}))

            if discount_line_ids:
                inv_vals.update({'global_discount_lines':[(6,0,discount_line_ids)]})
        return inv_vals