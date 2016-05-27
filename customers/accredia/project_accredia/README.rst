Personalizzazioni del modulo Project per Cliente Accredia
=========================================================

Questo modulo contiene tutte le funzionalità che riguardano la pianificazione in genere,
partendo dalle tabelle definite nel modulo dell'anagrafica (hr_accredia) e modificando
o personalizzando le funzioni proprie dell'area Project di Odoo.


Richieste di Accreditamento
---------------------------

Le Richieste di Accreditamento sono definite col modello accreditation.request e sono
il primo step di tutto il processo di accreditamento.


Pratiche
--------

Per Accredia, la dicitura "Project" o "Progetto" è stata rinominata in "Pratica".
Ogni pratica ha specificato un Tipo (modello accreditation.project.type) a seconda che
si tratti di un "Nuovo Accreditamento", un "Rinnovo", una "Estensione", ecc...

Una pratica ha inizio quando una Richiesta di Accreditamento viene accettata.


Team
----
La definizione dei team è a due livelli:
 - Team a livello di Pratica
 - Team a livello di Attività (accreditation.task.team)


Abilita'/Skill
--------------

Modello accreditation.skill, consente di specificare quali sono le abilità di ciascuna
persona fisica.


Autorizzazioni e dipendenti PA
------------------------------

Ogni persona fisica che sia dipendente PA puo avere autorizzazioni.
Il modello che mette in relazione le persone fisiche con tali autorizzazioni è
accreditation.persons.auth


Norme, Schemi e Settori
-----------------------

Per una spiegazione sulle modifiche che coinvolgono Norme, Schemi e Settori, si rimanda
alla documentazione funzionale.

Di seguito i modelli introdotti:
 - Norme: accreditation.standard
 - Schemi: accreditation.request.schema
 - Settori: accreditation.sector e accreditation.sector.category


Raggruppamento Attività
-----------------------

Tramite una label (accreditation.project.task.grouping), definibile in ciascuna attività, 
è possibile raggruppare attività in fase di copia delle attività stesse.
In tal modo è possibile rappresentare un workflow tramite la creazione di una serie di attività.
Supponiamo di voler creare un workflow che abbia la rappresentazione come un grafo che contenga dei cicli.
In tal caso, è possibile raggruppare le attività di un ciclo, in modo tale da gestire correttamente la copia delle attività.


Verifica compatibilità e disponibilità ispettori
------------------------------------------------
Meeting e Calendario:
 - la tabella dei meeting è quella fornita da Odoo base: calendar.event;


Pianificazione Audit
--------------------

La pianificazione e la successiva creazione delle attività di Audit è gestita in project.phase.


Gestione Elenco Prove
---------------------

Si rimanda al documento elenchi_prove.odt

