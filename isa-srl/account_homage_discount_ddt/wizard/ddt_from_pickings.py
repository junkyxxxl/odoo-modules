# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#    Copyright (C) Francesco Apruzzese
#    Copyright (C) 2014 Agile Business Group (http://www.agilebg.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp import fields
from openerp import models
from openerp import api
from openerp import _
from openerp.exceptions import Warning


class DdTFromPickingsDiscount(models.TransientModel):

    _inherit = "ddt.from.pickings"

    @api.multi
    def create_ddt(self):          
        
        t_discounts_list = []
        if self.picking_ids and self.picking_ids[0].sale_id.global_discount_lines:
            for line in self.picking_ids[0].sale_id.global_discount_lines:
                t_discounts_list.append((line.name.id,line.value))
        
        for picking in self.picking_ids:
            t_disc = []
            if picking.sale_id and picking.sale_id.global_discount_lines:
                for line in picking.sale_id.global_discount_lines:
                    t_disc.append((line.name.id,line.value))
                
                
            if len(t_discounts_list) != len(t_disc):
                raise Warning(_("Selected Pickings refers to sales orders with different global discounts"))
            for i in range(0,len(t_disc)):
                if t_disc[i] != t_discounts_list[i]: 
                    raise Warning(_("Selected Pickings refers to sales orders with different global discounts"))   

        res = super(DdTFromPickingsDiscount, self).create_ddt()
        return res
