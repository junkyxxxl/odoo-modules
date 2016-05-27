# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.exceptions import Warning

class res_company(models.Model):

    _inherit = "res.company"

    discount_untaxed_account_id = fields.Many2one('account.account', string='Discount Untaxed Account', help="The account used for untaxed discount")
    discount_tax_account_id = fields.Many2one('account.account', string='Discount Tax Account',  help="The account used for tax discount")
    homage_untaxed_account_id = fields.Many2one('account.account', string='Homage Untaxed Account', help="The account used for untaxed homage")
    homage_tax_account_id = fields.Many2one('account.account', string='Homage Tax Account', help="The account used for homage")
    homage_tax_id = fields.Many2one('account.tax', string='Homage Tax', help="The tax used for homage")
    homage_goods_account_id = fields.Many2one('account.account', string='Homage Goods Account', help="The account used for homage")
