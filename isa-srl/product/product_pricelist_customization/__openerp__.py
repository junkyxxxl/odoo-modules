# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2015 ISA srl (<http://www.isa.it>)
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
    'name': 'Product pricelist customization',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """
Product Pricelist Customization
Dipende dal modulo terze-parti 'purchase_discount'.
================================================================================
Questo modulo introduce il concetto di priorià nelle versioni di listino e 
definisce 3 livelli di sconto sugli ordini di vendita e sulle fatture, il cui 
valore è legato ai listini allo stesso modo in cui è legato ai listini il prezzo
unitario.

Tali funzionalità hanno un impatto notevole, in particolare, nella gestione del 
ciclo attivo (ordini di vendita e fatturazione in uscita).

================================================================================

PRIORITA' SUI LISTINI:

- DESCRIZIONE:
  La gestione di base dei listini, in Odoo, prevede che ad ogni listino (sia 
  esso di vendita o di acquisto) sia associato un numero indefinito di versioni
  (all'interno delle versioni sono poi definite le regole), con l'unico vincolo
  che tra tutte le versioni di un listino ne sia valida sempre e soltanto una 
  (ciò equivale a dire che i periodi di validità delle versioni attive non 
  possono sovrapporsi). 
  Inoltre, al momento del reperimento di un prezzo da listino, il sistema tiene in 
  considerazione le sole regole definite nella versione attualmente attiva.
  Infine, Odoo consente la creazioni di versioni aventi 
  periodo di validità illimitato (non impostando la data di inizio, la data di 
  fine o entrambe).
  
  Evidentemente, qualora un listino abbia una versione di durata illimitata (ed
  è spesso il caso, poiché la versione "di default" è generalmente settata con 
  durata illimitata) risulta impossibile inserire ulteriori versioni. 
  Ciò rende estremamente macchinoso, ad esempio, la creazione di versioni di 
  listino promozionali di durata limitata (bisogna agire, oltre che sulla 
  versione promozionale, anche su quella di default, limitandone temporaneamente
  la validità o rendendolo temporaneamente inattivo; inoltre è necessario 
  prestare particolare attenzione nel ripristinare la versione di default al
  termine della promozione per non incorrere in una situazione in cui il listino
  non abbia alcuna versione attiva in un certo periodo). 
  Inoltre, anche qualora si decidesse di percorrere questa strada, bisognerebbe 
  riprodurre, nella nuova versione, una regola per ognuna delle regole 
  appartenenti alla versione di default. Ciò comporterebbe, oltre che un lavoro 
  immenso per l'operatore, anche un appesantimento generale del DB (tradotto in 
  un degradamento delle prestazioni) ed una insensata duplicazione delle 
  informazioni.
  
  La soluzione trovata a questa problematica sta nel dotare ciascuna versione di
  listino di un valore di priorità e dunque consentire la sovrapposizione 
  temporale di due versioni dello stesso listino purché abbiano differente 
  priorità.
  Inoltre, facendo in modo che il sistema reperisca, per ogni prodotto, sempre
  la prima regola congruente tra tutte le sue versioni attualmente valide, 
  facilita immensamente la creazione di versioni specific-purpose contenenti 
  regole per anche solo una manciata di prodotti.

- CONFIGURAZIONE:
  L'ordine di priorità è decrescente: una versione con priorità più alta sarà 
  sempre presa in considerazione prima di una versione con priorità più bassa.
  
  Il range di priorità va da 0 ad un numero positivo virtualmente infinito.
  
  Le versioni già presenti sul sistema all'installazione di questo modulo 
  otterranno automaticamente un livello di priorità 10.
  
  Alla creazione di una nuova versione di listino, è richiesto di inserire
  il suo valore di priorità. Qualora tale valore non venisse impostato, il 
  sistema vi assegnerà automaticamente il valore 10.
  
  E' ora possibile far sovrapporre temporalmente due o più versioni attive,
  purché abbiano livelli di priorità differenti.

- UTILIZZO E FUNZIONAMENTO:
  L'utilizzo è del tutto trasparente all'utente, il quale non dovrà fare altro
  che (come già avveniva in precedenza) associare un listino ai propri partner.
  
  Ogniqualvolta il sistema deve reperire il prezzo di un prodotto passando dai
  listini (e ciò avviene, ad esempio, sugli ordini di vendita e di acquisto), 
  cerca, tra tutte le versioni attualmente attive del listino selezionato, tutte
  le regole valide per quel prodotto e prende quella appartenente alla versione
  con priorità più alta. Una volta ricavata la regola, il calcolo del prezzo 
  avviene in maniera del tutto analoga a quanto avveniva in precedenza.
  
================================================================================

SCONTI MULTIPLI SUI LISTINI:

- DESCRIZIONE:
  Alcune realtà imprenditoriali considerano un valore aggiunto l'opportunità di 
  dare evidenza, ai propri clienti, delle percentuali di sconto che concorrono 
  al calcolo del prezzo unitario dei singoli prodotti.
  In particolare, tali realtà desiderano poter indicare a livello di listino 
  fino a 3 percentuali di sconto (da applicare l'uno dopo l'altro al prezzo
  base) e che queste siano automaticamente riportate sulle righe di quegli 
  ordini di vendita e di quelle fatture che utilizzano il suddetto listino.
  
- CONFIGURAZIONE:
  Per ciascun utente a cui si intende abilitare questa funzionalità, è richiesto
  di aderire al gruppo "Sconti multipli sulle righe" ("Multiple discounts on
  lines"), spuntando l'omonimo flag in configurazione utente (nella tab
  'Autorizzazioni accesso', nella sezione 'Configurazioni Tecniche').
  
  Gli utenti abilitati potranno vedere, nella schermata delle regole di listino,
  i tre nuovi campi 'Sconto1', 'Sconto2' e 'Sconto3' (valorizzati a 0 di 
  default). 
  Gli stessi utenti saranno poi in grado di vedere, sia sulle righe degli ordini
  di vendita, sia  sulle righe di fattura, le tre nuove colonne ('Sconto1', 
  'Sconto2' e 'Sconto3') che sostituiscono la colonna 'Sconto %'. 
  
- UTILILIZZO E FUNZIONAMENTO:
  I tre nuovi campi di sconto, sulle righe di ordini di vendita e fatture in
  uscita, hanno un funzionamento del tutto trasparente rispetto al funzionamento
  standard del sistema poiché il loro unico utilizzo è quello di essere composti
  fino a calcolare un unico valore di sconto (ad esempio: eseguire uno sconto 
  del 30%, seguito da uno sconto del 20%, seguito da uno sconto del 10%, 
  equivale a fare un unico sconto del 49,6%) che viene assegnato al campo 
  'discount' (reso, invisibile all'utente, e pertanto non modificabile), 
  utilizzato da tutte le funzionalità di base. 
  
  Quando viene selezionato un prodotto, sulle righe degli ordini di vendita o di
  fattura in uscita, il sistema ricerca (analogamente a quanto fa per ricavare 
  il prezzo unitario) la regola di listino applicabile a quel prodotto; se su 
  tale regolai tre campi di scontistica sono valorizzati, questi sono 
  automaticamente riportati sulla riga d'ordine o di fattura. Ciò non impedisce, 
  comunque, all'utente di modificare/impostare manualmente tali scontistiche.
""",
    'author': 'ISA srl',
    'depends': ['account',
                'account_makeover',
                'product',
                'purchase',
                'purchase_discount',
                'sale',
                'stock',
                'sale_stock',
                ],
    'data': [
             'security/discount_security.xml',
             'views/pricelist_view.xml',
             'views/sale_order_view.xml',
             'views/purchase_order_view.xml',
             'views/account_invoice_view.xml',
             ],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
