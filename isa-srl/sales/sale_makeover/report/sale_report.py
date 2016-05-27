# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import tools
from openerp.osv import fields, osv

class sale_report_type_document(osv.osv):
    _inherit = "sale.report"


    _columns = {
        'document_type_id': fields.many2one('sale.document.type', 'Tipo Documento', readonly=True),
    }
    
    def _select(self):
        select_str = super(sale_report_type_document,self)._select()
        select_str = select_str + """,
                    s.document_type_id as document_type_id
        """
        return select_str

    def _group_by(self):
        group_by_str = super(sale_report_type_document,self)._group_by()
        group_by_str = group_by_str + """,
                    s.document_type_id
        """
        return group_by_str


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
