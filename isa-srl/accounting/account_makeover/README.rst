.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License

Account Makeover
================
Contiene le modifiche al modulo account sviluppate da ISA srl.

Calcolo IVA al salvataggio fattura
----------------------------------

Quando viene salvata o modificata la fattura viene calcolata automaticamente
l'IVA senza dover necessariamente cliccare sul tasto aggiorna.


Personalizzazioni con aggiunta del conto del cliente        
----------------------------------------------------

Il campo Banca Cliente si riferisce solo ai conti bancari del cliente.
Il campo Banca Azienda si riferisce solo ai conti bancari dell'azienda.

Memorizzazione riferimenti nelle registrazioni contabili
--------------------------------------------------------

Il modulo memorizza nelle registrazioni contabili i riferimenti
al numero ed alla data del documento che le hanno generate.
Ad esempio per le fatture fornitori memorizza il numero assegnato
alla fattura stessa dal fornitore e la data in cui è stata emessa.
Ciò permette una maggiore chiarezza nella comunicazione con la contro parte.
I due campi possono essere utili anche in registrazioni
non relative a documenti con Iva come assegni, disposizioni bancarie, ecc.

Numero Conto Automatico
-----------------------

Alla creazione di un conto sul pdc il modulo recupera in AUTOMATICO
il codice del mastro e gruppo selezionati e propone l'ultimo
progressivo numerico disponibile (comunque editabile).

Anteprima Scadenze
------------------

L'anteprima delle scadenze è la lista dei pagamenti che ci si aspetta
in fase di creazione di una fattura.
Il modulo aggiunge una nuova tab nella fattura (visibile solo in stato
di bozza). Tale tab mostra un promemoria delle scadenze di pagamento.

Stampa Fattura Immediata/Differita
----------------------------------

Il nome del file di stampa di una fattura contiene il numero fattura (con
l'underscore al posto dei caratteri non alfanumerici).


Ritenute d'acconto sulle fatture fornitore
------------------------------------------
Il presente modulo non dipende dal modulo della Community
l10n_it_withholding_tax poiché la funzionalità per la gestione delle
Ritenute d'acconto è stata riscritto da zero.
Si sconsiglia pertanto l'installazione di l10n_it_withholding_tax.

In fase di installazione del modulo, la tabella account.withholding.tax.isa
viene popolata con dati iniziali.

Per utilizzare il modulo bisogna configurare i seguenti campi:
1) Nella scheda del fornitore va impostato il codice della ritenuta d'acconto.
2) Nella scheda del prodotto va impostato il flag Soggetto a Ritenuta d'Acconto.

Dal menu Accounting->Configuration->Accounts->Withholding Tax
si possono modificare le impostazioni per le Ritenute d'Acconto.
1) codice ritenuta acconto (5 cifre)
2) aliquota (xxx.yy)
3) imponibile (xxx.yy)
4) descrizione
5) codice conto di debito per le ritenute da versare (es. erario c/rit.acconto)
6) account journal : collegamento a account_journal

Nella fattura fornitore, è possibile che solo alcune delle righe dei prodotti
siano soggette a rda. In tal caso il valore della Ritenuta d'Acconto
è calcolato automaticamente dal totale fattura, così come il Netto a pagare.

Il calcolo dell'importo della ritenuta è eseguito automaticamente alla
pressione del pulsante Update.
Tuttavia viene mantenuta la possibilità di modificare a mano
l'importo della rda.

Nella vista della fattura, in basso, sono anche riepilogati codice,
aliquota e imponibile della rda per il fornitore.

Se nel partner non è specificato il codice della rit. d'acconto allora
rimane tutto invariato (non si applica la rit. d'acconto).

Quando la fattura viene validata viene creato il movimento contabile per la rda.

In fase di installazione del modulo, il termine di pagamento del 16 del
mese successivo viene aggiunto nella tabella dei termini di pagamento ed
utilizzato per calcolo della scadenza del pagamento della rda.
Se il pagamento non è ancora creato, nel calcolo della scadenza del pagamento
della rda si considera la data di scadenza della fattura.


Gestione Automatica Sottoconti
------------------------------

Il modulo dispone delle funzionalità di generazione automatica 
dei sottoconti al momento della creazione di un nuovo cliente/fornitore.
Per abilitare queste funzionalità occorre andare sulla tab configurazione dell'azienda.
Nella tab configurazione dell'azienda, andare nella parte Generazione Sottoconti.
Qui sono presenti 2 flag: 
- Generazione Automatica Sottoconti Clienti
- Generazione Automatica Sottoconti Fornitori
Spuntando i flag si dovrà scegliere il mastro per i sottoconti, 
solitamente 15 per il conto clienti e 25 per il conto fornitori.


Generazione note credito fornitori per fatture in bozza
-------------------------------------------------------

Questo modulo permette la generazione automatica di una nota di credito fornitore
a partire da una fattura fornitore anche in stato bozza.
E' possibile generare solo una nota di credito per ogni fattura in bozza, mediante
il pulsante 'Richiesta nota di credito' nella pagina della specifica fattura.

