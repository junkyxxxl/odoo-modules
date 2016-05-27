# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, orm


class res_partner(orm.Model):
    _inherit = 'res.partner'

    _columns = {
        'supplier': fields.boolean('Supplier'),
        'carrier_flag': fields.boolean('Carrier',
                            help="Check this box if this contact is a carrier"),

        'delivery_methods': fields.selection([('sender', 'Sender '),
                                              ('receiver', 'Receiver'),
                                              ('carrier', 'Carrier')],
                                             'Trasporto a cura',
                                             select=True,
                                             translate=True),
        'carrier_id': fields.many2one('delivery.carrier',
                            'Trasportatore Abituale'),

        # Delivery Options
        'one_order_one_draft': fields.boolean('One Order Per Draft',
                            help="If checked one order per draft"),

        'one_product_one_draft': fields.boolean('One Product Per Draft',
                            help="if checked one product per draft"),

        'print_values': fields.boolean('Print Values',
                            help="if checked print values"),

        'attach_qc_documents': fields.boolean('Attach QC Documents',
                            help="If checked attach quality documents "),

        'document_copies': fields.integer('Document Copies',
                            help="Number of document copies"),

        'packing_notes' : fields.text('Additional Information'),
    }

    def onchange_carrier_flag(self, cr, uid, ids, supplier, carrier_flag):
        if(not supplier and carrier_flag):
            return {'value': {'supplier': True,
                    }
            }
        return {'value': {'supplier': supplier,
                        }
        }
