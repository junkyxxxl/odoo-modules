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
    'name': 'Family Commission Primapaint',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'description': """

Questo modulo esegue delle personalizzazioni sulla gestione delle provvigioni, 
legate alle famiglie di prodotto, per il cliente Primapaint.

================================================================================   

CONFIGURAZIONE:

Questo modulo aggiunge un nuovo livello di calcolo provvigioni, legato alle 
famiglie. Per inserire di fatto tale livello nell'ordine di priorità (nonché per 
definirne la priorità), selezionare l'azienda desiderata dal menù 
'Configurazione' -> 'Aziende' -> 'Aziende' e, nella tab 'Salesagent & Commissions',
ridefinire i 5 (non più 4) livelli di priorità.

Per definire le percentuali di provvigione associate alle famiglie, andare nel
menu 'Magazzino' -> 'Configurazione' -> 'Prodotti' -> 'Qualificatori Prodotto'
e selezionare il qualificatore (di tipo famiglia) desiderato.
Nella visualizzazione di ciascun qualificatore di famiglia è ora possibile 
valorizzare il campo 'Commission [%]' che rappresenta la percentuale di 
provvigione standard per tutti i prodotti afferenti alla famiglia corrente.

Se si desidera applicare provvigioni differenti per clienti speciali (ovvero
facenti parte di una categoria considerata speciale), si può selezionare una
categoria di clienti nel campo 'Categoria Cliente', selezionare una voce 
nella lista di categorie suggerite farà apparire il campo 'Special Commission [%]'
in cui è possibile specificare la percentuale di provvigione spettante agli agenti
che completano delle vendite riguardanti prodotti della famiglia corrente ad un
cliente appartenente alla categoria selezionata.

Infine, nella visualizzazione della famiglia, è possibile definire una serie di 
soglie di sconto collegate ad altrettante percentuali di provvigione. Tali righe
vengono visualizzate, automaticamente, ordinate per soglia di sconto (in ordine 
crescente). 
La soglia massima di sconto indica la percentuale di extra-sconto massimo che un 
agente può applicare su un prodotto della famiglia corrente (ovvero lo sconto 
ulteriore applicabile una volta che lo sconto per famiglia, associato al cliente,
sia già stato applicato). Qualora non sia presenta alcuna soglia, o qualora il 
cliente faccia parte della categoria speciale per questa famiglia, non è 
per nulla possibile applicare un extra-sconto.
Qualora siano presenti delle righe, allora l'agente è abilitato
ad applicare un extra-sconto (entro il limite massimo consentito); lo sconto 
applicato viene confrontato con le differenti soglie ed all'agente viene 
riconosciuta la percentuale di provvigione collegata alla soglia minima cui
lo sconto applicato rientra.

================================================================================   
    
""",
    'author': 'ISA srl',
    'depends': [
                'product_family_discount',
                'product_pricelist_customization',
                'product_family',
                'product_show_pricelists',
                'sale',
                'account',
                'partner_attributes',
                'account_commission',                
                ],
    'data': [
             'security/ir.model.access.csv',
             'views/pricelist_view.xml',  
             'views/product_family_view.xml', 
             'views/res_company_view.xml',             
             'views/account_invoice_view.xml',
             'views/sale_order_view.xml',   
             'views/res_partner_view.xml',
             'data/update_lst_price.xml',
             ],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}
