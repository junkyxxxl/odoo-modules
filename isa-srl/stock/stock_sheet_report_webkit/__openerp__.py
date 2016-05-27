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

{
    'name': 'Warehouse Stock Sheet Report',
    'version': '0.1',
    'category': 'Warehouse',
    'description': """
Warehouse - Warehouse manager
=============================

Aggiunge il riferimento al picking che la genera sulla riga di fattura.

Mostra il riferimento al DDT, nel caso si crea un ordine di vendita
e la fattura viene generata "su ordine di consegna" (impostando
il campo "crea fattura").


Creazione Fattura Accompagnatoria
---------------------------------
Dal menu Configurazione-> Magazzino impostare:
Create and open the invoice when the user finish a delivery order

Quando da un Ordine di Consegna si sceglie "Conferma", appare
una popup di conferma per la generazione della fattura accompagnatoria.


Fattura Magazzino layout
------------------------
Il nome del file di stampa di una fattura contiene il numero fattura
(con l'underscore al posto dei caratteri non alfanumerici).

Configurazione->Technical->Azioni->Reports->Stampa Fattura Accompagnatoria


""",
    'author': 'ISA srl',
    'depends': [
                'stock',
                'stock_makeover',
                'report_webkit',
                ],
    'data': [
             'data/stock_webkit_header.xml',
             'report/reports.xml',
             'wizard/wizard_stock_sheet_view.xml',
             'wizard/wizard_stock_sheet_result_view.xml',
             'menu_actions.xml',
             ],

    'demo': [],
    'test': [],
    'installable': True,
    'certificate': '',
}
