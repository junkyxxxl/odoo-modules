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

from openerp.osv import fields,orm


class ricerca_riba(orm.TransientModel):
    _name = "riba.ricerca.cliente"
    _description = "Ricerca Ricevute Bancarie"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'due_date' : fields.date("Data Scadenza"),                
        'line_ids': fields.many2many('riba.distinta.line',string='Linee Ri.Ba.'),
        }
    
    def onchange_partner_id(self, cr, uid, ids, partner_id, due_date, context=None):
        if not partner_id:
            return
        domains = []
        domains.append(('partner_id','=',partner_id))
        if due_date:
            domains.append(('due_date','=',due_date))
        ids = self.pool.get('riba.distinta.line').search(cr, uid, domains)
        return {'value':{'line_ids': [(6,0,ids)]}}
        