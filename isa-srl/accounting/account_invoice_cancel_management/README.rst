

Cancellazione fatture validate
==============================

Questo modulo consente di eliminare fatture validate (ma non ancora pagate).

Quando si crea una nuova fattura è possibile forzare il numero fattura,
scegliendolo tra quelli già assegnati in precedenza per una delle fatture
eliminate.


Configurazione
--------------

Affinché sia possibile eliminare fatture già validate è necessario
impostare il sezionale della fattura mettendo a true i seguenti campi:
- Consenti cancellazione registrazioni
- Consenti la forzatura diretta del numero fattura
- Permetti di forzare il numero della fattura scegliendo tra i numeri dalle fatture cancellate

L'utente deve essere abilitato alla cancellazione abilitando il gruppo:
- Account Invoice Cancel Management Customer

Per cancellare una fattura validata
-----------------------------------

- Annullare la registrazione contabile, passando dallo stato Confermato a Non Pubblicate
- Annullare la fattura tramite l'apposito pulsante Cancella Fattura
- Nel menu Altro cliccare su Elimina

Per rimpiazzare una fattura cancellata
--------------------------------------

Per rimpiazzare una fattura cancellata in precedenza:
- Creare una fattura in bozza e salvare
- In Recupera Numero impostare una tra le vecchie fatture cancellate
- Se necessario rivedere il valore in Forza Numero Protocollo

