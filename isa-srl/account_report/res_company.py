# -*- coding: utf-8 -*-
from openerp import models, fields


class res_company(models.Model):

    _inherit = ['res.company']

    print_contacts = fields.Boolean(
        string='Print contacts',
        help='Print contacts in ddt header'
    )

    disclaimer = fields.Text(string='Disclaimer')

    privacy_info = fields.Text(string='Privacy info')

    invoice_notes = fields.Text(
        string='Invoice notes',
        help='Notes that will be print as the first line in invoice body'
    )

    print_location_information = fields.Boolean(
        string='Print location information',
        help='''if selected , you will print the locations moves.
        Valid only for DDT.'''
    )
