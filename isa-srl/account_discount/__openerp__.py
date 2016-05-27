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
    'name': "Global Discounts",
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
    
Questo modulo implementa la gestione di scontistiche globali negli ordini di 
vendita e nelle fatture.

================================================================================    
    
INTRODUZIONE:

Per sconto globale si intende uno sconto che, definito una volta, agisce su 
tutte le righe di un documento (nel nostro caso, il documento può essere un
ordine di vendita o una fattura). Poiché tale sconto agisce allo stesso modo su 
tutte le righe del documento, lo si può anche vedere come uno sconto che agisce
direttamente sul totale imponibile del documento stesso.

Alcuni esempi comuni di sconti globali sono quelli legati ai termini di 
pagamento: un'azienda può decidere di applicare uno sconto globale a tutti gli 
ordini di quei clienti che decidono di pagare con termini vantaggiosi 
all'azienda (ad esempio in contanti); un altro caso comune è quello di  sconti 
globali legati ai partner: l'azienda potrebbe stringere un accordo con un 
partner al fine di concedergli uno sconto globale che sarà applicato su  tutti 
i suoi ordini.

================================================================================

CONFIGURAZIONE:

In seguito all'installazione del modulo, va eseguita un'operazione di 
configurazione su quei prodotti relativamente ai quali si intende non applicare 
gli sconti globali. Per ottenere ciò, si entri nella schermata del prodotto su 
cui si desidera intervenire e, nella tab "Informazioni", spuntare il flag "No 
Discounts".

Vanno dunque create le tipologie di sconto: accedere al menù 'Contabilità' -> 
'Configurazione' -> 'Tipologie di Sconto' e creare tanti record quante 
differenti tipologie di sconto si intende gestire. Una tipologia di sconto 
si caratterizza per un nome ed un tipo che può essere percentuale (lo sconto
verrà applicato in percentuale sull'imponibile delle righe d'ordine) o fisso 
(lo sconto sarà applicato come valore fisso al totale del documento).

E' possibile, inoltre, configurare su partner (nella tab 'Vendite e Acquisti')
e termini di pagamento (menù 'Contabilità -> Configurazione -> Varie -> Termini
di pagamento), una lista di sconti globali. Tali sconti globali saranno 
impostati, di default, su tutti gli ordini di vendita o le fatture relative al
partner configurato oppure su cui è applicato il termine di pagamento
configurato.
 
================================================================================

UTILIZZO:

Alla creazione di un ordine di vendita o di una fattura, nella stessa tab in 
cui sono elencate le righe del documento, è ora presente anche una lista degli
sconti globali. In tale lista, l'utente può inserire gli sconti globali 
selezionando, per ciascuno di essi, un nome (legato alle tipologie di sconto
precedentemente configurate), un valore ed un tipo (di default sarà suggerito
il tipo della tipologia di sconto selezionato).

Quando un ordine di vendita a cui sono legati degli sconti globali viene
fatturato, la fattura risultante avrà già automaticamente valorizzati gli 
stessi sconti globali dell'ordine di vendita di partenza.
Inoltre, a causa di questa propagazione degli scontri da ordini di vendita
a fatture, nei casi di fatturazione di più ordini di vendita (ad esempio
a partire da picking o DDT), la procedura di fatturazion considererà gli 
sconti globali come discriminante per il raggruppamento.

""",
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "depends" : ['account',
                 'sale',
                 'stock',
                 'stock_account',
                 'free_invoice_line',
                 'l10n_it_ddt_makeover',
                ],
    "data" : ['security/ir.model.access.csv',
              'sale/sale_order_view.xml',
              'account/account_invoice_view.xml',
              'account/account_discount_view.xml',
              'account/account_payment_term_view.xml',
              'product/product_view.xml',
              'res/res_partner_view.xml',
              'company/company_view.xml',
             ],
    "demo" : [],
    "installable": True
}
