# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_partner(models.Model):

    _inherit = ['res.partner']

    salesagent_target_count = fields.Integer(
        string='# of Salesagent Target',
        compute=lambda self: self._target_count()
    )

    salesagent_target_ids = fields.One2many(
        string='Salesagent target history',
        comodel_name='salesagent.target',
        inverse_name='salesagent_id',
    )

    @api.one
    @api.depends('salesagent_target_count')
    def _target_count(self):
        targets = self.env['salesagent.target'].search([('salesagent_id', '=', self.id)])
        self.salesagent_target_count = len(targets)
