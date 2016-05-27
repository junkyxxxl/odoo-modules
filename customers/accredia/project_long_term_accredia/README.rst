Modulo per la gestione degli Audit
==================================

Nella versione Openerp 7.0 esisteva di base il modulo project_long_term.
In Odoo 8.0 tale modulo è stato rimosso.

Il modulo project_long_term_accredia è semplicemente il porting
del modulo project_long_term da Openerp 7.0 a Odoo 8.0.

Quello che faceva il vecchio modulo project_long_term era di introdurre il concetto di "fase" per la gestione dei progetti.
Per Accredia, la parola "Fase" è stata sostituita da "Audit". Un Audit è una sorta di contenitore di Attività.
In pratica un progetto contiene Attività e Fasi. Le Fasi a loro volta contengono ulteriori Attività

