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
    'name': 'Product family Discount',
    'version': '0.1',
    'category': '',
    'description': """
    
INTRODUZIONE:
    
Questo modulo implementa la gestione di un valore di sconto personalizzato per
partner, relativamente ad una specifica istanza di un classificatore (famiglia,
sottofamiglia, etc.).

================================================================================    
    
CONFIGURAZIONE:

IMPORTANTE: Questo modulo si basa sulla funzionalità di sconti multipli su 
listino, introdotta dal modulo 'product_pricelist_customization'; Installando 
questo modulo,  il terzo valore di sconto sui listini viene rimosso. 

Appena installato il modulo è necessario configurare, a livello di azienda, qual
è il classificatore. Accedere al menù 'Configurazione' -> 'Utenti' -> 'Aziende' 
-> 'Aziende', selezionare l'azienda da configurare e recarsi nella tab 
'Configurazione' e nella sezione 'Vendite' valorizzare il campo 'Family type
filter' selezionando il classificatore su cui si desidera configurare gli sconti.

Per configurare uno sconto relativo all'entità di un classificatore su un 
partner, accedere alla schermata di un partner ed andare nella tab 'Vendite e 
Acquisti'. Nella sezione 'Classifier Discount', è ora presente una lista in cui 
è possibile aggiungere una nuova regola selezionando l'entità del classificatore
su cui applicare lo sconto e valorizzando il campo sconto.

Se si desidera impostare ad un partner esattamente le stesse regole di sconto 
già applicate ad un altro partner, è possibile dalla schermata del partner 
destinatario clickare sul pulsante "Duplicate discounts from other partner" e 
selezionare il partner sorgente oppure a partire dalla schermata del partner 
sorgente clickare sul pulsante "Duplicate discounts on other partner" e 
selezionare il partner (o i partner, in questo caso è consentita la selezione
multipla) destinatario.

================================================================================

UTILIZZO:

Una volta configurate le regole di sconto per classificatore su un partner, è 
sufficiente creare un documento (ordine di vendita, di acquisto o fattura) 
relativo a tale partner ed inserire righe normalmente. Ogni volta che verrà 
inserita una riga, relativamente ad un prodotto appartenente ad uno dei 
classificatori per cui esiste una regola, il sistema valorizzerà in automatico
il campo 'Sconto 3" con la percentuale di sconto configurata per quel partner
per quel classificatore.

""",
    'author': 'ISA srl',
    'depends': ['product',
                'sale',
                'account',
                'product_family',
                'product_pricelist_customization',
                ],
    'data': [
             'security/ir.model.access.csv',
             'views/res_partner_view.xml',
             'views/res_company_view.xml',
             'views/pricelist_view.xml',
             'wizard/wizard_duplicate_discounts.xml',
             'wizard/wizard_family_discount_view.xml',
             'views/product_family_discount_view.xml'
             ],

    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
