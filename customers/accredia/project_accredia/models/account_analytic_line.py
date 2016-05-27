# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.one
    def _get_fnct_amount(self):
        self.fnct_amount = self.amount
        if self.amount < 0.0:
            self.fnct_amount = -self.amount

    task_id = fields.Many2one('project.task', 'Riferimento')
    fnct_amount = fields.Float(compute='_get_fnct_amount', string="Importo")
