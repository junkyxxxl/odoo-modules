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
    'name': 'Account Commission',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """

Questo modulo introduce la gestione degli agenti di vendita e delle provvigioni.

================================================================================    
    
INTRODUZIONE:

L’agente di commercio è un libero professionista che assume l’incarico di 
stabilire contratti commerciali di vendita tra l’azienda committente ed i 
clienti potenziali, in base ad un contratto di agenzia che lo vincola a 
determinati limiti (inclusi, generalmente, limiti geografici entro cui può 
operare) ed obiettivi.

Il compenso spettante all’agente di commercio è definito provvigione ed è 
solitamente calcolato sulla base di una percentuale predeterminata sul fatturato
 prodotto per il mandante.

La percentuale di provvigione è generalmente indicata nel contratto di agenzia 
ed è valido per tutte le vendite eseguite dall’agente, tuttavia possono esistere
eccezioni legate ai singoli clienti oppure ai prodotti/servizi oggetto della 
vendita: nell’accordo tra azienda committente ed agente può essere deciso che 
per determinati clienti o per determinati prodotti/servizi, la percentuale di
provvigione dovuta all’agente sia più alta o più bassa di quella che gli è 
generalmente corrisposta.

Una provvigione si definisce maturata nel momento in cui è pronta per essere 
liquidata (ovvero corrisposta all’agente); le condizioni di maturazione delle 
provvigioni sono definite nel contratto d’agenzia e ricadono, generalmente, in 
due casi:
- Sul fatturato: quando il contratto di vendita viene accettato e firmato sia 
dal cliente che dall’azienda committente;
- Sull’incassato: quando l’azienda committente ha ricevuto il pagamento della 
vendita effettuata dal suo agente (in base ai termini di pagamento ciò può 
avvenire anche molto tempo dopo che la vendita è stata terminata);

Talvolta può avvenire che ad un agente operante in una certa zona (capo-area) 
siano legati uno o più agenti (sub-agenti) i quali eseguono le vendite per suo 
conto. In tal caso, la provvigione corrisposta dall’azienda committente viene 
diviso tra capo-area e sub-agente secondo percentuali predeterminate e legate 
all’accordo tra i due agenti.

================================================================================
 
CONFIGURAZIONE:


Innanzitutto va creato almeno un prodotto provvigione:
- Creare un prodotto di tipo ‘servizio’ e spuntare il flag ‘Provvigione’;
- Assegnarvi una categoria adeguata (già esistente o creata apposta);
- Assegnarvi i conti di costo e di ricavo;

- Vanno poi settati dei parametri a livello di azienda:
- Nella tab ‘agenti e provvigioni’ della vista relativa all’azienda, settare i 
campi ‘priorità provvigione’ (1,2,3,4);
- Nella stessa tab, scegliere un prodotto da assegnare al campo ‘Prodotto per 
Provvigione’;’

Al momento della creazione di un agente, seguire i passi seguenti:
- Creare un utente ed assegnargli i gruppi ‘Portale’ ed ‘Agente di Commercio’;
- Andare nella vista del partner associato all’utente;
- Nella tab ‘Vendite e Acquisti’ Settare il flag ‘Agente’;
- Nella tab ‘Agente’ Selezionare la ‘Modalità maturazione provvigioni’ 
desiderata, settare un valore in ‘Provvigione agente [%]’ ed inserire un 
‘Codice agente’;
- Scegliere inoltre un prodotto da assegnare al campo ‘Prodotto per Provvigione’;
- Nella tab ‘Agente’, qualora si voglia assegnare un capo area a questo agente, 
selezionare un agente nel campo ‘Capo-Area’ ed assegnare un valore al campo 
‘Provvigione capo-area [%]’;


Qualora si vogliano associare delle regole specifiche per il reperimento delle 
provvigioni:
- Nella tab 'Agente', Spuntare il flag 'L'agente sovrascrive le  regole di 
default per le provvigioni'; 
- Nella lista 'Provvigioni  Personalizzate', inserire tante regole quante se ne 
desiderano avendo cura di settare un qualsiasi insieme dei parametri richiesti; 
ricordare che qualora uno o più parametri non venissero impostati, il sistema 
non filtrerà su tale parametro (se non viene impostato un 'Cliente', la regola
sarà valida per tutti i clienti); per tale motivo può essere creata una regola 
globale avendo cura di impostare il solo campo di 'Provvigione [%]'; 
- Riordinare, mediante trascinamento, la priorità delle regole così create. 
In fase di reperimento delle provvigioni, le regole saranno sempre valutate in 
ordine ed in maniera prioritaria rispetto a quelle definite sull'azienda.

Qualora si desiderino assegnare delle percentuali di provvigione specifiche su 
clienti/categorie prodotto/prodotto, impostare i relativi campi:
- ‘Provvigione cliente [%]’ nella tab ‘vendite e acquisti’ in vista clienti;
- ‘Provvigione categoria [%]’ in vista categorie prodotto;
- ‘Provvigione prodotto [%]’ nella tab ‘vendite’ in vista varianti prodotto;

Qualora si desideri disabilitare il calcolo delle provvigioni su uno specifico 
articolo o categoria di articolo, impostare a True i relativi flag:
- ‘No Provvigione’ nella vista varianti prodotto;
- ‘No Provvigione’ nella tab ‘vendite’ in vista varianti prodotto;

Per assegnare un agente ad un cliente, impostare il seguente campo:
- ‘Agente’ nella tab ‘Vendite e Acquisti’ in vista cliente;

================================================================================

UTILIZZO:

Creazione di ordini di vendita (fatture):

Alla creazione di un ordine di vendita (fattura), nel momento in cui viene 
selezionato un partner, viene automaticamente assegnato al campo ‘Commerciale’ 
l’utente relativo all’agente assegnato al partner (è comunque possibile 
modificare tale valore impostando un agente differente alla vendita in corso). 

Per ogni riga d’ordine (fattura) inserita, viene automaticamente reperita la 
percentuale di provvigione da riconoscere all’agente sulla base di tutta una 
serie di parametri che comprende le percentuali di provvigione impostate 
sull’agente, sul cliente, sul prodotto e sulla categoria del prodotto, valutate 
nell’ordine di priorità impostato in configurazione aziendale. Tale valore resta
comunque modificabile manualmente da parte dell’utente.

Al salvataggio dell’ordine (fattura), vengono automaticamente ricalcolati ed 
aggiornati i valori di ‘Importo provvigione’ di tutte le righe aggiunte o 
modificate (o di tutte nel caso in cui siano cambiati i valori di sconto 
globale);

Si ricorda che una nota di credito è di fatto una fattura, per cui adotta il 
medesimo comportamento individuato dalla fattura.

Fatturazione ordini di vendita:

Nel processo di fatturazione ordini di vendita (sia direttamente che passando da
picking/DDT), le fatture create saranno automaticamente raggruppate per agente e
vedranno il campo ‘Commerciale’ nonché i campi ‘Percentuale Provvigione’ e 
‘Importo Provvigione’ delle sue righe, già valorizzati con gli stessi valori 
impostati nell’ordine di provenienza.

Tale meccanismo funziona in maniera analoga nel processo di creazione di note di
credito.

Nel caso di fatturazione differita, qualora si intendessero raggruppare picking 
di uscita (che darebbe origine ad una fattura di vendita) e di ingresso (merce 
stornata che darebbe origine ad una nota di credito a cliente), il documento 
risultante sarebbe una fattura di vendita con alcune righe (quelle relative ai 
movimenti di storno) a subtotale negativo, pertanto anche i valori di 
provvigione automaticamente calcolati avranno un valore negativo.

Calcolo e Maturazione delle provvigioni:

Nel momento in cui una fattura di vendita (o nota di credito a cliente) viene 
validata, il sistema calcola automaticamente le provvigioni riconosciute agli 
agenti, eseguendo un’elaborazione su tutte le righe aventi una percentuale di 
provvigione diversa da 0. 
Le provvigioni così calcolate sono visualizzabili in un’apposita vista a lista 
in cui si dà evidenza di informazioni quali l’agente, il cliente, la riga di 
fattura e la fattura di provenienza, la data di fatturazione e l’importo della 
provvigione e dell’imponibile su cui è stata calcolata. 
Qualora la provvigione sia stata calcolata per un sub-agente, si calcola la 
parte effettivamente spettante al sub-agente e quella spettante al suo 
capo-area, il sistema crea due righe di provvigione in questo caso.

Tali righe non sono mai modificabili direttamente dall’utente che può soltanto 
cambiarne indirettamente lo stato attraverso l’utilizzo di funzionalità fornite 
dal sistema.

Le righe vengono automaticamente create in stato ‘Calcolato’ e vengono portate 
allo stato ’Maturato’ al verificarsi di determinate condizioni legate alle 
condizioni di maturazione impostate sull’agente:
Alla creazione della riga stessa, qualora la maturazione sia sul fatturato;
Al pagamento della fattura d’origine, qualora la maturazione sia sull’incassato;

Fatturazione delle provvigioni:

Dalla vista a lista delle provvigioni è possibile selezionare un qualsiasi 
numero di righe di provvigione in stato ‘Maturato’ e richiamare la funzionalità 
di ‘Fattura Provvigioni’ (impostando eventualmente la data di fatturazione e 
l’opzione di separazione per fattura).

Il sistema raggruppa eventualmente le righe selezionate in base all’agente (e 
separando eventualmente in base alla fattura di origine qualora sia stata 
spuntata tale opzione) e per ciascun raggruppamento crea una fattura a fornitore
(oppure una nota di credito a fornitore, se il raggruppamento contiene solo 
righe provenienti da una nota di credito a cliente), in cui il fornitore è 
l’agente stesso e che contiene tante righe quante sono le righe di provvigione 
che fanno parte del raggruppamento. Ciascuna riga di fattura viene associata al 
prodotto di provvigione configurato a livello agente (o eventualmente a livello 
azienda), contiene nella descrizione riferimenti alla riga della fattura di 
provenienza, ha quantità 1 e prezzo unitario pari all’importo di provvigione a 
cui fa riferimento.

Le righe di provvigione da cui è partita questa operazione prendono dunque lo 
stato ‘Fatturato’;

Pagamento delle provvigioni:

Il pagamento delle provvigioni consiste semplicemente nel pagamento delle 
fatture a fornitore a cui sono associate e viene fatto seguendo i 
meccanismi già presenti nel sistema. Quando una fattura a fornitore cambia il 
suo stato in ‘Pagato’, anche le righe di provvigione associate assumono questo 
stato.

Annullamento e cancellazione delle provvigioni:

E’ possibile eliminare le sole righe di provvigione in stato ‘Annullato’;
E’ possibile annullare le sole righe di provvigione in stato ‘Calcolato’ o 
‘Maturato’;
E’ possibile riportare una riga di provvigione dallo stato ‘Fatturato’ a 
‘Maturato’ annullando ed eliminando la fattura agente a cui è collegata;
Non è possibile annullare righe di commissione già pagate;
""",
    'author': 'ISA srl',
    'depends': ['account',
                'product',
                'sale',
                ],
    'data': [
             'security/commission_security.xml',             
             'security/ir.model.access.csv',
             'views/account_invoice_view.xml',
             'views/account_invoice_workflow.xml',
             'views/res_partner_view.xml',
             'views/product_product_view.xml',
             'views/res_company_view.xml',
             'views/account_commission_view.xml',
             'views/sale_order_view.xml',
             'wizard/wizard_invoice_commission_view.xml',
             'views/account_menuitem.xml',             
             ],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
