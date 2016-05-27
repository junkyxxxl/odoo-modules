# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2011-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
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
    'name': 'Registri IVA - Webkit Report',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """
Report Registri IVA - Webkit
============================

Report Registri IVA - Italian localization
            
http://wiki.openerp-italia.org/doku.php/moduli/l10n_it_tax_journal
            
            """,
    'author': ['ISA srl','OpenERP Italian Community'],
    'website': 'http://www.openerp-italia.org',
    'license': 'AGPL-3',
    "depends" : ['report_webkit',
                 'account_financial_report_webkit',
                 'l10n_it_base',
                 'base_fiscalcode',
                 'account_vat_registries_report',
                 ],
    "data" : [
              'security/ir.model.access.csv',
              'data/vat_registries_webkit_header.xml',
              'report/reports.xml',
              'security/vat_registries_group.xml',
              'wizard/print_registro_iva.xml',
              'wizard/reset_protocol_numbers.xml',
              'wizard/wizard_post_reset_view.xml',
             ],
    'conflicts': [
        'l10n_it_vat_registries',
    ],
    "demo" : [],
    "active": False,
    "installable": True
}
