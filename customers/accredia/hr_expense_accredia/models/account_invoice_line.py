# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    task_id = fields.Many2one('project.task', 'Audit')
    expense_line_id = fields.Many2one('hr.expense.line', 'Riga Nota Spese')
    project_id = fields.Many2one(related='task_id.project_id',
                                 comodel_name="project.project",
                                 store=False, string="Pratica", readonly=True)
