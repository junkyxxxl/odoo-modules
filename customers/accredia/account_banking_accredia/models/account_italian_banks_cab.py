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

from openerp import fields, models


class AccountItalianBanksCab(models.Model):
    _name = 'account.italian.banks.cab'

    abi = fields.Char(related='code',
                      comodel_name='account.italian.banks.abi',
                      string='ABI',
                      store=True,
                      readonly=True)
    code = fields.Char('Code', size=5)
    name = fields.Char('Description', size=250)
    cap = fields.Char('CAP', size=5)
    agency = fields.Char('Agency', size=250)
    address = fields.Char('Address', size=250)
    city = fields.Char('City', size=40)
    province = fields.Char('Province', size=2)
    # il campo "Aggiornamento" evidenzia la data
    # di riferimento di validità dei dati.
    date = fields.Date('Date')
