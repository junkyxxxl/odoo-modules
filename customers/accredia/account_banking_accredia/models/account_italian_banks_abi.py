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


class AccountItalianBanksAbi(models.Model):
    _name = 'account.italian.banks.abi'

    code = fields.Char('Code', size=5)
    name = fields.Char('Description', size=250)
    date = fields.Date('Date')
    status = fields.Selection([('0', 'Banca attiva'),
                               ('1', 'Banca non più attiva'),
                               ('2', ' - - - '),
                               ],
                              string='Status',
                              size=1)
    # Il campo sostituto nel caso di banca non attiva (stato = 1) contiene
    # il codice abi della banca che ha assorbito gli sportelli
    substitute = fields.Char('Sostituto', size=27)
