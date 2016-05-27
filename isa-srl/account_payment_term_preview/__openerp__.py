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
{
    'name': "Account Payment Term Preview",
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
Questo modulo implementa l'anteprima delle date di scadenze sulle fatture.
Su una fattura, anche non ancora validata (e su cui, dunque, le date di scadenza
non sono state ancora calcolate, è presente una nuova stampa (richiamabile anche
da pulsante nel menù pulsanti) di tipo HTML che mostra quali saranno le scadenze
(data di scadenza, importo e tipo di pagamento) qualora la fattura venisse 
validata senza ulteriori modifiche.
""",
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "depends" : ['account',
                 'account_makeover',
                 ],
    "data" : [
              'views/account_invoice_view.xml',
              'views/report_invoice_payment_term_preview.xml',
              'report.xml',
             ],
    "demo" : [],
    "installable": True
}
