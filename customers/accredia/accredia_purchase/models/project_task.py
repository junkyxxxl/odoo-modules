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


class ProjectTask(models.Model):

    _inherit = "project.task"

    purchase_order_ids = fields.One2many('purchase.order', 'task_id', 'Preventivi/Ordini')

    @api.multi
    def case_close(self):

        res = super(ProjectTask, self).case_close()

        for task in self:
            if task.phase_id:
                # conferma preventivi fornitori

                for t_order in task.purchase_order_ids:
                    if t_order.state == 'draft':
                        t_order.signal_workflow('purchase_confirm')
                    elif t_order.state == 'sent':
                        t_order.signal_workflow('purchase_approve')
        return res
