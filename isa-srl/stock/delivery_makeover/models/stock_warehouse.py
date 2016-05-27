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
from openerp import SUPERUSER_ID


class stock_warehouse(orm.Model):

    _inherit = 'stock.warehouse'

    def create(self, cr, uid, vals, context=None):

        res_id = super(stock_warehouse, self).create(cr, uid, vals=vals, context=context)

        seq_obj = self.pool.get('ir.sequence')
        picking_type_obj = self.pool.get('stock.picking.type')
        warehouse_data = self.browse(cr, uid, res_id, context=context)

        seq_dict = {
            'company_id': warehouse_data.company_id and warehouse_data.company_id.id or None,
            'implementation': 'no_gap',
            'number_increment': 1,
            'name': "DDT Sequence " + warehouse_data.name,
            'number_next': 1,
            'number_next_actual':1,
            'padding': '',
            'prefix': 'DDT%(year)s',
            'suffix': '',
            }

        ddt_seq_id = seq_obj.create(cr, SUPERUSER_ID, values=seq_dict, context=context)

        picking_type_obj.write(cr, uid,
                               warehouse_data.out_type_id.id,
                               vals={'ddt_sequence_id': ddt_seq_id},
                               context=context)

        return res_id
