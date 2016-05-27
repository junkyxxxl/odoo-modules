# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Andrea Cometa.
#    Email: info@andreacometa.it
#    Web site: http://www.andreacometa.it
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
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
    "name": "Ricevute Bancarie",
    "version": "1.3",
    "author": ["ISA srl", "OpenERP Italian Community"],
    "category": "Accounting & Finance",
    "website": "http://www.openerp-italia.org",
    'images': [],
    'depends': ['account',
                'account_makeover',
                'account_voucher',
                'base_fiscalcode',
                'base_iban',
                'account_due_list',
                'report',
                ],
    'data': ['security/ir.model.access.csv',
             'data/report_paperformat.xml',    
             'data/riba_sequence.xml',
             'data/riba_workflow.xml',
             'wizard/wizard_accreditation.xml',
             'wizard/wizard_unsolved.xml',
             'wizard/wizard_emissione_riba.xml',
             'wizard/wizard_ricerca_riba_cliente.xml',
             'wizard/riba_file_export.xml',
             'views/partner_view.xml',
             'views/riba_configurazione_view.xml',
             'views/riba_distinta_view.xml',
             'views/account_move_line_view.xml',
             'views/account_view.xml',
             'views/report_riba.xml',
             'report/report.xml',
             'menu_actions.xml',
             ],
    'conflicts': ['l10n_it_ricevute_bancarie',
                  ],
    'demo': [],
    'test': [],
    'installable': True,
    'active': False,
}
