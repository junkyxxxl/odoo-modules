
Account Voucher Makeover
========================
This is the customization for the account_voucher module, developed by ISA srl.


Ritenute d'acconto sulle fatture fornitore
------------------------------------------
Il presente modulo non dipende dal modulo della Community
l10n_it_withholding_tax poiché la funzionalità per la gestione delle
Ritenute d'acconto è stata riscritto da zero.
Si sconsiglia pertanto l'installazione di l10n_it_withholding_tax.

Quando la fattura con rda viene validata viene creato il movimento
contabile per la rda.
In fase di pagamento della fattura, cliccando su "Paga" direttamente dalla
fattura, l'ammontare è automaticamente visualizzato come netto a pagare e
non come totale della fattura.

In fase di installazione del modulo, il termine di pagamento del 16 del
mese successivo viene aggiunto nella tabella dei termini di pagamento ed
utilizzato per calcolo della scadenza del pagamento della rda.
Se il pagamento non è ancora creato, nel calcolo della scadenza del pagamento
della rda si considera la data di scadenza della fattura.


Pagamenti a partire dagli Estratti Conto
----------------------------------------

Il modulo estende gli Estratti Conto per permettere il pagamento
di una fattura a partire da un estratto conto aperto.
Nella schermata con l'estratto conto aperto è presente il bottone che
apre la schermata dei pagamenti.


Abbuoni
-------
Tramite questo modulo è avere gli abbuoni nella gestione dei pagamenti
verso i fornitori e degli incassi dai clienti.
Dopo aver installato il modulo, bisogna impostare i campi presenti in
Configurazione->Aziende->My company->Configurazione (TAB).
In particolare occorre definire due conti sotto la tab configurazione 
dell'azienda, uno per gli abbuoni passivi e l'altro per gli abbuoni attivi.


Pagamenti Fornitori
-------------------
Tramite questo modulo è possibile effettuare i pagamenti dei fornitori per fatture
fornitori validate.
E' possibile effettuare pagamenti interi, parziali e con abbuoni.
Inoltre è possibile selezionare pagamenti da effettuare relativi a diversi fornitori.
Per effettuare un pagamento selezionare la voce 'Pagamento' sotto il menù fornitori
della Contabilità. 
Per effettuare i pagamenti occore definire almeno un conto bancario aziendale.


Incassi da Clienti
------------------
Tramite questo modulo è possibile effettuare gli incassi da clienti per fatture
clienti validate.
E' possibile effettuare incassi interi, parziali e con abbuoni.
Inoltre è possibile selezionare pagamenti da effettuare relativi a diversi clienti.
Per effettuare un incasso selezionare la voce 'Incassi' sotto il menù clienti
della Contabilità.
Per effettuare i pagamenti occore definire almeno un conto bancario aziendale.


Cambio Scadenze
---------------
Tramite questo modulo è possibile cambiare le scadenze a partire da fatture validate
o da una movimentazione legata ad una fattura.
Il pulsante per il cambio scadenze è presente sotto la tab Scadenze di una fattura
o nella pagina di una Movimentazione.
Non è possibile cambiare scadenze di movimentazioni Ri.Ba., tuttavia è possibile 
creare una scadenza Ri.Ba., a partire da una movimentazione generica,
se la banca del partner è definita nella fattura.

