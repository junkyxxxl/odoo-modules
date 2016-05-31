# -*- coding: utf-8 -*-
from openerp import fields, models, api

class WizardChangeDueDate(models.TransientModel):

    _inherit = 'wizard.change.due.date'

    amount_to_complete = fields.Float(string="Amount To Add")

    @api.onchange('new_ids')
    def calculate_amount_to_complete(self):
        new_ids = self.new_ids
        old_ids = self.old_ids
        total_new = 0.00
        total_old = 0.00
        for n in new_ids:
            total_new+= n.amount
        for n in old_ids:
            total_old+= n.amount
        self.amount_to_complete=total_old-total_new

