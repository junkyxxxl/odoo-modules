# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015
#    Andrea Gallina <a.gallina@apuliasoftware.it>
#    WEB (<http://www.apuliasoftware.it>).
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

from openerp import models, fields, api, _

class ProductCategory(models.Model):

    _inherit = "product.category"

    def category_map(self, categ_id, list_ids=[]):
        list_ids.append(categ_id.id)
        if categ_id.child_id:
            for child in categ_id.child_id:
                if child.child_id:
                    self.categoy_map(child, list_ids)
                else:
                    list_ids.append(child.id)
        return list_ids