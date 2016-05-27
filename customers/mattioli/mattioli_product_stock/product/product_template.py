# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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


class product_template_mattioli(osv.osv):
    _inherit = "product.template"

    _columns = {
        'is_wood': fields.boolean('Is Wood'),
        'is_shipping': fields.boolean('Spedizione'),
        'essence': fields.many2one('res.essence', 'Essence'),
        'seasoning': fields.many2one('res.seasoning', 'Seasoning'),
        'wood_type': fields.many2one('res.wood.type', 'Wood Type'),
        'wood_quality': fields.many2one('res.wood.quality', 'Wood Quality'),
        'finiture': fields.many2one('res.finiture','Finitura'),
        'thickness': fields.float('Thickness [cm]'),
        'increment_thickness': fields.float('Increment Thickness'),
        'increment_length': fields.float('Increment Length'),
        'increment_width': fields.float('Increment Width'),        
        'increment_uom_thickness': fields.selection([('cm', 'Centimetres [cm]'),
                                           ('percent', 'Percentual [%]')],
                                          string='Increment type'),
        'increment_uom_length': fields.selection([('cm', 'Centimetres [cm]'),
                                           ('percent', 'Percentual [%]')],
                                          string='Increment type'),
        'increment_uom_width': fields.selection([('cm', 'Centimetres [cm]'),
                                           ('percent', 'Percentual [%]')],
                                          string='Increment type'),                
    }

    _defaults = {'is_wood': False,
                 'increment_thickness': 0,
                 'increment_uom_thickness': 'percent',
                 'increment_length': 0,
                 'increment_uom_length': 'percent',
                 'increment_width': 0,
                 'increment_uom_width': 'percent',
                 'is_shipping': False,
                 'type':'product',
                 }

    def onchange_is_wood(self, cr, uid, ids, flag, context=None):
        values = {}
        if not flag:
            values['essence'] = None
            values['seasoning'] = None
            values['wood_type'] = None
            values['wood_quality'] = None
            values['finiture'] = None
            values['thickness'] = None
            values['increment_thickness'] = 0
            values['increment_uom_thickness'] = 'percent'
            values['increment_length'] = 0
            values['increment_uom_length'] = 'percent'
            values['increment_width'] = 0
            values['increment_uom_width'] = 'percent'
        return {'value': values}
