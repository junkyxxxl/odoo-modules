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
from openerp.tools.translate import _


class product_product(orm.Model):

    _inherit = "product.product"

    def onchange_uom_secondary(self, cr, uid, ids, uom_id, uom_po_id, uom_secondary):
        res = {'value': {}}
        if uom_secondary and uom_id != uom_secondary:
            uom_data = self.pool.get('product.uom').browse(cr, uid, uom_id,
                                                           context=None)
            uom_secondary_data = self.pool.get('product.uom').browse(cr, uid, uom_secondary, context=None)
            if uom_data.category_id.id != uom_secondary_data.category_id.id:
                res['warning'] = {'title': _('Warning'),
                                  'message': _('Selected Unit of Measure does not belong to the same category as the product Unit of Measure. Secondary UoM Coefficient value is mandatory.')}
                res['value'].update({'uom_id': uom_id,
                                     'uom_po_id': uom_po_id,
                                     'uom_secondary': uom_secondary,
                                     })
        return res

    def onchange_uom(self, cr, uid, ids, uom_id, uom_po_id):
        if uom_id:
            return {'value': {'uom_po_id': uom_id,
                              'uom_secondary': None,
                              }
                    }
        return {}

    _columns = {
        # Nomenclatura combinata - numerico 9
        'combined_nomenclature': fields.many2one('account.cee.combined.nomenclature',
                                                 'Combined Nomenclature'),
        # Codice servizio - numerico 6
        'service_codes': fields.many2one('account.cee.service.codes',
                                         'Nomenclatura combinata per servizi'),
        # Massa netta - numerico 10
        'net_mass': fields.float('Net Mass'),
        # Valore statistico
        'statistical_value': fields.float('Statistical Value'),
        # Un.misura supplementare - numerico  10
        'uom_secondary': fields.many2one('product.uom',
                                         'Secondary Unit of Measure'),
        # Coefficiente Un.misura supplementare
        'uom_secondary_coeff': fields.float('Secondary UoM Coefficient'),
        }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        if 'tmpl_combined_nomenclature' in context:
            vals.update({'combined_nomenclature': context['tmpl_combined_nomenclature']})

        if 'tmpl_service_codes' in context:
            vals.update({'service_codes': context['tmpl_service_codes']})

        if 'tmpl_net_mass' in context:
            vals.update({'net_mass': context['tmpl_net_mass']})

        if 'tmpl_statistical_value' in context:
            vals.update({'statistical_value': context['tmpl_statistical_value']})

        if 'tmpl_uom_secondary' in context:
            vals.update({'uom_secondary': context['tmpl_uom_secondary']})

        if 'tmpl_uom_secondary_coeff' in context:
            vals.update({'uom_secondary_coeff': context['tmpl_uom_secondary_coeff']})

        return super(product_product, self).create(cr, uid, vals, context)
