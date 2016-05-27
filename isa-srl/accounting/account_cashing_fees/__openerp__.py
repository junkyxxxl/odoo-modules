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
    'name': "Cashing Fees",
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
Questo modulo implementa la gestione delle spese d'incasso nelle fatture.
La spesa d'incasso viene implementata come un prodotto, opportunamente 
configurato, che sarà inserito tra le righe della fattura.

In questo modulo si fa l'assunzione che le spese d'incasso siano definite a
livello aziendale e che siano dunque valide per tutti i clienti.

================================================================================

DESCRIZIONE:

La gestione delle spese d'incasso ha l'obiettivo di addebitare nel ciclo attivo 
dell'azienda i costi che quest'ultima deve sostenere quando presenta in banca la
distinta delle ricevute bancarie accumulate nel proprio portafoglio effetti. Nel
documento di vendita viene concordato con il cliente la modalità di pagamento, e
nel caso di Ri.Ba., si dovrà addebitare un determinato importo tante volte per 
quante scadenze darà origine la fattura.

Esempio: per un totale fattura di 100€ con pagamento Ri.Ba. 30/60 gg, gli
addebiti da calcolare nel documento saranno due.

Bisogna però fare attenzione ad alcuni casi che si possono verificare:

- Non vanno addebitate al cliente le spese d'incasso nel caso di generazione di
  una scadenza che ha la data uguale ad un'altra già presente nel portafoglio
  effetti da emettere. In sintesi, se un cliente fa più acquisti in un
  determinato periodo, sempre con le stesse condizioni di pagamento, l'addebito
  dovrà essere fatto solo sulla prima fattura.
  
- Potrebbe verificarsi che un cliente effettui in un determinato periodo 2
  acquisti, uno con pagamento Ri.Ba. 30 gg e l'altro con Ri.Ba. 30/60 gg. Il 
  programma dovrà addebitare nella prima fattura un recupero spese relativo alla
  scadenza a 30 gg, nella seconda un altro recupero spese relativo solo alla
  scadenza dei 60 gg, in quanto le spese d'incasso per la scadenza dei 30 gg (che
  coincide con quella della prima fattura) sono già stati addebitati nella prima 
  fattura.
  
- Qualora non sia previsto, per un dato cliente, il raggruppamento delle Ri.Ba.,
  si intende che ogni fattura debba avere le proprie ricevute e pertanto è 
  necessario calcolare le spese d'incasso senza tenere in considerazione quanto
  esposto precedentemente.

Dev'essere in ogni caso possibile, per un'azienda, decidere di accollarsi 
interamente le spese d'incasso destinate ad un cliente in particolare o persino
a tutti i suoi clienti.

================================================================================

CONFIGURAZIONE:

- Creare un prodotto da utilizzare come spesa d'incasso:
  Il prodotto va creato come servizio, gli va assegnato un conto di ricavo 
  appropriato e va associato ad una categoria adatta (ricordare che in assenza 
  del conto di ricavo sul prodotto, questi verrà preso dalla categoria).
  Si ricorda di dover impostare le imposte e si consiglia di valorizzare il 
  campo 'Prezzo di vendita' anche nel caso in cui si gestiscano i prezzi di 
  vendita mediante listini (ed in tal caso, creare delle regole per il prodotto
  appena creato).
  Infine, nella tab 'Informazioni', va spuntato il flag 'Spesa d'incasso'.
  
- Impostare le spese d'incasso a livello di azienda:
  Nella form di configurazione azienda, nella form 'Configurazione', sotto il
  paragrafo 'Contabilità', valorizzare il campo 'Articolo spese d'incasso' col 
  prodotto creato in precedenza. 
  Qualora non venisse selezionato alcun articolo, si assume che l'azienda abbia
  deciso di accollarsi le spese d'incasso di tutti i propri clienti.
  
- Evidenziare i clienti esenti da spese d'incasso:
  Nella form dei clienti che si intende esentare dal pagamento delle spese 
  d'incasso, nella tab 'Contabilità', spuntare il flag 'No Spese d'incasso'.
  
================================================================================

UTILIZZO E FUNZIONAMENTO:

Una volta completata la fase di configurazione, il modulo funziona in maniera del
tutto automatica.

In creazione fattura, qualora sia stato selezionato un cliente che deve pagare le
spese d'incasso ed un termine di pagamento che preveda almeno una scadenza con 
tipo di pagamento Ri.Ba., al salvataggio della fattura il sistema andrà a 
reperire il prodotto spese d'incasso configurato a livello di azienda ed andrà a
verificare se e quante spese d'incasso il cliente dovrà pagare ed eventualmente 
inserirà una riga aggiuntiva che riporta il prodotto (comprensivo di prezzo,
imposta e conto contabile così come configurati) con la quantità calcolata.

In modifica di una fattura, qualora avvenisse il cambio di partner, data di 
fatturazione o termini di pagamento, la riga di spese d'incasso eventualmente 
già presente verrebbe automaticamente rimossa ed, eventualmente, sostituita da 
una nuova riga calcolata dal sistema sulla base dei nuovi parametri.

""",
    'author': 'ISA srl',
    'website': 'http://www.isa.it',
    'license': 'AGPL-3',
    "depends" : ['account',
                 'account_ricevute_bancarie',
                 'account_makeover',
                 'product',
                ],
    "data" : [
              'views/product_view.xml',
              'views/res_partner_view.xml',
              'views/res_company_view.xml',
             ],
    "demo" : [],
    "installable": True
}
