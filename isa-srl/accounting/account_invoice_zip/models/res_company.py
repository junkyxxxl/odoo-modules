# -*- coding: utf-8 -*-
from openerp import models, fields, api


class res_company(models.Model):
    _inherit = 'res.company'

    invoice_report = fields.Many2one('ir.actions.report.xml', string="Report fatture", required = True)
