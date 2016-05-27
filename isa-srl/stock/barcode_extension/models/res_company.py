# -*- coding: utf-8 -*-
from openerp import models, fields


class res_company(models.Model):

    _inherit = ['res.company']

    larger_amount = fields.Boolean(string="Quantita evasa maggiore di richiesta", required=False)
    article_not_available = fields.Boolean(string="Articolo non presente in lista", required=False)
    confirmation_article_not_available = fields.Boolean(string="Richiesta conferma per articolo non presente in lista", required=False)
    picking_list_type_id = fields.Many2one(comodel_name='stock.picking.type')
    check_quantity = fields.Boolean(string="Controlla quantità richieste")
    force_check_quantity = fields.Boolean(string="Abilita forzatura su controllo quantità in evasione ordine")
