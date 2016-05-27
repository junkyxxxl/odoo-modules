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

from openerp import fields, models, api


class ProductProduct(models.Model):

    _inherit = 'product.product'

    expense_type = fields.Selection([('car_own', 'Rimborso Auto Propria'),
                                     ('car_rent', 'Noleggio Auto'),
                                     ('airplane_train', 'Aereo/Treno'),
                                     ('public_transport', 'Metro/Taxi'),
                                     ('restaurant', 'Ristorante/Bar'),
                                     ('hotel', 'Hotel'),
                                     ('parking', 'Parcheggio'),
                                     ('highway', 'Pedaggio Autostradale'),
                                     ('other', 'Altro')],
                                    string='Tipo di Spesa')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):

        if not self.env.context.get('own_car_use', False) and self.env.context.get('check_car_use', False):
            args = args + [['expense_type', '!=', 'car_own']]

        return super(ProductProduct, self).name_search(name=name, args=args, operator=operator, limit=limit)
