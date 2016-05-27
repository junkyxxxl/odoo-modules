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


class res_partner(osv.osv):

    _inherit = "res.partner"
    
    def _get_internal_standard_ids(self, cr, uid, ids, field_name, arg, context=None):
        r = {}
        for id in ids:
            d = '[0,'
            for link in self.browse(cr,uid,id,context=context).standard_ea_rel_ids:
                d = d+str(link.standard_id.id)+','
            d = d + '0]'
            r[id] = d
        return r
    
    
    _columns = {
        'standard_ea_rel_ids': fields.one2many('standard.sector.link', 'partner_id', string='Norme e Settori'),
        'internal_standard_ids': fields.function(_get_internal_standard_ids, type='char', string='Standard ids per Domain', readonly=1, store=True),
    }

    _defaults = {
        'notify_email': 'none',
    }
