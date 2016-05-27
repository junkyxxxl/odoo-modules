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

from openerp import fields, models, api
from openerp.tools.translate import _


class VatRegistries(models.Model):
    _name = "vat.registries.isa"
    _description = "Vat Registries Type"

    name = fields.Char('Nome', size=64, required=True)
    layout_type = fields.Selection([('customer', 'Vendite'),
                                    ('supplier', 'Acquisti'),
                                    ('corrispettivi', 'Corrispettivi'),
                                    ], 'Layout Stampa')
    sequence_iva_registry_id = fields.Many2one('ir.sequence', 'Entry Sequence', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True)               
    period_id = fields.Many2one('account.period', 'Period', required=False, readonly=True)
    page = fields.Integer('Page Position', required=False, readonly=True, default=0)

    @api.onchange('sequence_iva_registry_id')
    def onchange_sequence_iva_registry_id(self):
        warning = {}
        if self.sequence_iva_registry_id:
            if self.sequence_iva_registry_id.prefix:
                warning = {'title': _('Warning!'),
                           'message': _('This sequence is not allowed because it contains a prefix')
                           }

            if self.sequence_iva_registry_id.suffix:
                warning = {'title': _('Warning!'),
                           'message': _('This sequence is not allowed because it contains a suffix')
                           }

        return {'value': {},
                'warning': warning,
                }
