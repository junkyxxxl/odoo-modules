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


class StockMove(orm.Model):
    _inherit = 'stock.move'

    def action_done(self, cr, uid, ids, context=None):

        res = super(StockMove,self).action_done(cr, uid, ids, context=context)

        moves_data = self.browse(cr, uid, ids)
        for move_data in moves_data:
            date = move_data.picking_id.date
            if date:
                self.write(cr, uid, move_data.id, {'date': date}, context=context)
        return res
