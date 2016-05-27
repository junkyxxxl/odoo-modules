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

from openerp.osv import fields, orm


class standard_sector_link(orm.Model):

    _name = "standard.sector.link"

    _columns = {
        'standard_id': fields.many2one('accreditation.standard',
                                       string='Norma',
                                       ondelete='cascade'),
        'ea_sector_ids': fields.many2many('accreditation.sector.ea',
                                          string='Settori EA'),
        'nace_sector_ids': fields.many2many('res.partner.category',
                                            string='Settori NACE'),
        'partner_id': fields.many2one('res.partner',
                                      string='Partner',
                                      ondelete='cascade'),
        }

    def onchange_ea_sector_ids(self, cr, uid, ids, sct):
        res = []
        sectors = sct[0][2]
        if sectors:
            nace_obj = self.pool.get('res.partner.category')
            ea_obj = self.pool.get('accreditation.sector.ea')
            for ea in sectors:
                ea_data = ea_obj.browse(cr, uid, ea)
                for rel_id in ea_data.related_nace_ids:
                    parent_id = rel_id.nace_parent_id.id
                    ids = nace_obj.search(cr, uid, [('parent_id', 'child_of', parent_id), ('is_leaf', '=', True)])
                    res.extend(ids)

        dom = {'nace_sector_ids':  [('id', 'in', res)]}
        return {'domain': dom}
        return None
