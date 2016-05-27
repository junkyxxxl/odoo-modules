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

from openerp.osv import orm


class account_invoice_cashing_fees(orm.Model):

    _inherit = 'account.invoice'

    def _get_tax_id(self, cr, uid, product, company_id, fpos, context=None):
        if 'exporter_id' in context and context['exporter_id']:
            taxes = self.pool.get('account.exporter.statements').browse(cr,uid,context['exporter_id'],context=context).vat_code_id
            tax_id = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes) 
        else:
            tax_id = super(account_invoice_cashing_fees,self)._get_tax_id(cr, uid, product, company_id, fpos, context=context)
        return tax_id       

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]       

        if 'exporter_id' in vals:
            ctx['exporter_id'] = vals['exporter_id']                                                
        return super(account_invoice_cashing_fees,self).create(cr, uid, vals, context=ctx)
        
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}

        ctx = {}
        for item in context.items():
            ctx[item[0]] = item[1]     

        curr_inv = self.browse(cr, uid, ids, context=context)
        
        if 'exporter_id' in vals:
            ctx['exporter_id'] = vals['exporter_id']          
        elif curr_inv.exporter_id:
            ctx['exporter_id'] = curr_inv.exporter_id.id
                                    
        return super(account_invoice_cashing_fees,self).write(cr, uid, ids, vals, context=ctx)