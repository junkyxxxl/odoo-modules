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


class AccountCeePaymentMethods(models.Model):

    _name = "account.cee.payment.methods"
    _rec_name = 'description'

# Modalità di incasso
# a) Indicare il codice B (bonifico) nel caso in cui il servizio ricevuto venga pagato mediante bonifico bancario.
# b) Indicare il codice A (accredito) nel caso in cui il servizio ricevuto venga pagato mediante accredito in conto corrente bancario.
# c) Indicare il codice X (altro) nel caso in cui il servizio ricevuto venga pagato in modalità diverse da quelle previste nei punti a) e b). 

    code_alpha = fields.Char('Code Alpha', size=1, required=True)
    description = fields.Text('Description', required=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            item_desc = (record.code_alpha or '') + ' - ' + (record.description or '')
            res.append((record.id, item_desc))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=80):
        if not args:
            args = []
        args = args[:]
        records = self.search(['|',
                               ('code_alpha', operator, name),
                               ('description', operator, name)] + args,
                              limit=limit)
        return records.name_get()
