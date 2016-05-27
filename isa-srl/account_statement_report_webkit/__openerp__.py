# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 ISA s.r.l. (<http://www.isa.it>).
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
    'name': 'Report Estratti Conto - Webkit',
    'description': """
Report Estratti Conto - Webkit
==============================

Il modulo basa la sua operatività sul concetto di partita; di un numero,
in sostanza, che raggruppi per fattura i movimenti a debito e a credito.

La funzione più importante consiste nel dare la possibilità di visualizzare
solo le "partite aperte" (le sole fatture da incassare/pagare),
solo le "partite chiuse" (le sole fatture incassate/pagate)
o "tutte le partite, facilitando  il controllo dei saldi
dei clienti/fornitori e differenziandosi così dalla gestione dei partitari
contabili ove i movimenti vengono gestiti in ordine di data di registrazione. 

""",
    'version': '0.1',
    'author': 'ISA srl',
    'license': 'AGPL-3',
    'category': 'Finance',
    'website': 'http://www.isa.it',

    'depends': ['account',
                'account_ricevute_bancarie',
                'account_invoice_intracee',
                'account_financial_report_webkit',
                'report_webkit'],

    'demo' : [],
    'data': [
               'data/financial_webkit_header.xml',
               'report/report.xml',
               'wizard/account_statement_wizard.xml',
               ],

    'test': [],

    'active': False,
    'installable': True,
    'application': True,
}
