# -*- coding: utf-8 -*-
# © <2016> <Isa>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class MailMailStatistics(models.Model):
    _inherit = ['mail.mail.statistics']

    resource_reference = fields.Reference(lambda self: [
        (m.model, m.name)
        for m in self.env['ir.model'].search([])
    ], string='Subject', compute="_get_resource", store=True)

    @api.multi
    @api.depends('model', 'res_id')
    def _get_resource(self):
        for record in self:
            if record.model and record.res_id:
                record.resource_reference = '%s, %d' % (record.model, record.res_id)
