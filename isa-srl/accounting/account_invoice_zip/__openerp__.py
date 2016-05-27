# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Export Invoice Zip',
    'version': '1.0',
    'category': 'Web',
    'license': 'AGPL-3',
    'description': """
        Estrazione zip pdf fatture - Il modulo permette di estrarre dalla vista a lista delle fatture uno zip contentente la stampa di tutte le fatture dei clienti selezionati
       """,
    'depends': [
        'web',
        'account',
        'pentaho_reports'
    ],
    'data': [
        'view/web_export_invoice_zip_view.xml',
    ],
    'qweb': [
        'static/src/xml/web_export_account_zip_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}
