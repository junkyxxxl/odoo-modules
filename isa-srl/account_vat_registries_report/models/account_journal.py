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


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    iva_registry_id = fields.Many2one('vat.registries.isa', 'VAT Registry')

    @api.onchange('iva_registry_id')
    def onchange_iva_registry_id(self):
        warning = {}
        if self.iva_registry_id:
            t_seq = self.iva_registry_id.sequence_iva_registry_id
            if t_seq and t_seq.prefix:
                warning = {'title': _('Warning!'),
                           'message': _('This sequence is not allowed because it contains a prefix')
                           }

            if t_seq and t_seq.suffix:
                warning = {'title': _('Warning!'),
                           'message': _('This sequence is not allowed because it contains a suffix')
                           }

        return {'value': {},
                'warning': warning,
                }
