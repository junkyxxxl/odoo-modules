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

from openerp import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    payment_reminder_issued = fields.Boolean('Payment Reminder Issued', default=False)
    reminder_state = fields.Selection([('draft', 'Draft'),
                                       ('selected', 'Selected'),
                                       ('sent', 'Sent')],
                                      default='draft',
                                      string='Reminder State')
    gamma_numreg_contab = fields.Char('Gamma Num. Reg.')
    gamma_numrata = fields.Char('Gamma Num. Rata', size=64)
    department_id = fields.Many2one(related='move_id.journal_id.department_id',
                                    comodel_name="hr.department",
                                    string="Dipartimento")
