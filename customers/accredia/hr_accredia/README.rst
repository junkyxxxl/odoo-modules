Accredia - Gestione Anagrafica Unificata
========================================
Questo modulo comprende le personalizzazioni del
modulo HR per Cliente Accredia, nell'ambito del progetto del
Sistema Centralizzato di Gestione Anagrafica Unificata.

In particolare:

Enti
----
Sono quei partner che hanno il flag is_entity = True.
Collegamenti:
 - Categorie Enti: definite nel modello accreditation.entity.categories
 - Indirizzi
 - Dipartimenti


Persone fisiche
---------------
Sono quei partner che hanno il flag individual = True.
 - Qualifiche: modello accreditation.qualifications
 - Ruoli: accreditation.roles


Incompatibilita'
----------------
Alcune persone fisiche (es.: alcuni ispettori) presentano incompatibilità con alcuni Enti.
Queste incompatibilità sono specificate nella relazione tra tra Persone e Unità, definite in accreditation.persons.entities
La motivazione di tale incompatibilità è specificato in accreditation.persons.entities.reason


Sedi e Unita'
-------------
Il presente modulo aggiunge inoltre i concetti di Sedi, Unità:
 - Sedi, definite in accreditation.locations
 - Unità, definite nel modello accreditation.units
 - Categorie Unità: modello accreditation.units.categories

Un ente può avere una o più Sedi. Ogni Sede è costituita da una o più Unità.

Ogni Unità è inoltre in relazione con le persone fisiche tramite la tabella accreditation.persons.units


Comitati
--------
Un Ente può avere un comitato.
I Componenti del comitato sono definiti nella tabella accreditation.institution.members



Changelog
---------
Le modifiche di Enti e Unità non sono ammesse. Nuovi Enti (o Unità) possono sostituire vecchi Enti (o Unità).
Per tener traccia di queste sostituzioni si usano i changelog, definiti nei modelli accreditation.changelog
e accreditation.unit.changelog
