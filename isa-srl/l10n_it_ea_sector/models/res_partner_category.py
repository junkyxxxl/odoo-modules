# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

class res_partner_category(osv.osv):

    _inherit = "res.partner.category"

    def _get_is_leaf(self, cr, uid, ids, name, args, context=None):
        res = {}
        for id in ids:        
            t = self.browse(cr,uid,[id]).child_ids
            if t:
                res[id] = False
            else:
                res[id] = True
        return res
            

    _columns = {
        'child_ids': fields.one2many('res.partner.category',
                                      'parent_id',
                                       string='Childs'),
        'is_leaf':fields.function(_get_is_leaf,
            type='boolean',
            store=True,
            string='Has Childs'),
    }