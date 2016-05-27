# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 ISA s.r.l. (<http://www.isa.it>).
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

{
    'name': 'Montecristo Salesagents Commission Report QWeb',
    'version': '0.1',
    'category': 'Reporting',
    'description': '''
Questo modulo gestisce correttamente la stampa delle provvigioni tenendo conto della gestione dei subagenti
sviluppata per il cliente Montecristo.
    ''',
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    'depends' : ['base',
                 'account',
                 'salesagent_commissions',
                 'salesagent_commissions_report_qweb',
                 'montecristo_salesagents_commissions',
                 'report',
                ],
    'data' : [
              'views/montecristo_report_commissions_qweb.xml',
              ],
    'demo' : [],
    'installable': True,
}
