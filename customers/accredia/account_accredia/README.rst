Accredia - Invoice on Timesheets
================================

Questo modulo funge da contenitore per le personalizzazioni che riguardano la contabilità per Accredia.



Solleciti clienti
-----------------

Questo modulo estende il modulo di Odoo account_followup che gestisce i Solleciti.
Tra le personalizzazioni fornite: gli utenti dell'amministrazione possono scegliere le
partite clienti scadute e non saldate per emettere le lettere di sollecito
secondo le procedure aziendali.
Le lettere saranno prodotte in formato PDF da un'apposita applicazione di Doclite.



Diritti di mantenimento
-----------------------

Il presente modulo getta le basi per la creazione degli ordini ed eventuali fatture per i Diritti
annui di Concessione Accreditamento.

La creazione vera e propria avviene tramite il pulsante "Esegui" Azione,
il cui funzionamento è definito nel modulo project_action_accredia.

Le configurazioni degli scaglioni, delle soglie minime, piccoli laboratori, ecc. sono possibili mediante le tabelle:
 - accreditation.group.charges
 - accreditation.invoiced.schema
 - accreditation.small.lab
 - res.company (nel gruppo di campi "Diritti di Mantenimento")
