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


class account_cee_invoice_lines(orm.Model):

    _inherit = "account.invoice.line"

    def _get_tot_net_mass(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            t_unit_net_mass = rec.unit_net_mass
            t_quantity = rec.quantity
            result[rec.id] = t_unit_net_mass * t_quantity
        return result

    def _get_tot_stat(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            t_unit_stat = rec.unit_statistical_value
            t_quantity = rec.quantity
            result[rec.id] = t_unit_stat * t_quantity
        return result

    def _get_qty_second_uom(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            t_quantity = rec.quantity
            result[rec.id] = t_quantity
            if rec.uom_secondary:
                if rec.uom_secondary.factor:
                    t_factor = rec.uom_secondary.factor
                    result[rec.id] = t_factor * t_quantity
                if rec.product_id.uom_secondary_coeff:
                    t_factor = rec.product_id.uom_secondary_coeff
                    result[rec.id] = t_factor * t_quantity
        return result

    def _is_intracee(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for rec in self.browse(cr, uid, ids, context=context):
            t_bool = False
            if (rec.invoice_id
                    and rec.invoice_id.fiscal_position
                    and rec.invoice_id.fiscal_position.name):
                t_name = rec.invoice_id.fiscal_position.name
                if (t_name == 'Regime Intra comunitario'):
                    t_bool = True
            result[rec.id] = t_bool
        return result

    def check_intracee(self, cr, uid, fiscal_position_id, context=None):
        t_bool = False
        c_fiscal_position_id = None
        if context and 'company_id' in context and context['company_id']:
            c_fiscal_position_id = self.pool.get('res.company').browse(cr, uid, context['company_id'], context=context).intracee_fiscal_position.id
        if fiscal_position_id:
            fiscal_position_obj = self.pool.get('account.fiscal.position')
            for rec in fiscal_position_obj.browse(cr, uid, [fiscal_position_id]):
                if rec.id == c_fiscal_position_id:
                    t_bool = True
        return t_bool

    _columns = {
            'combined_nomenclature': fields.related('product_id',
                                                    'combined_nomenclature',
                                                    type="many2one",
                                                    relation="account.cee.combined.nomenclature",
                                                    readonly=True,
                                                    string='Combined Nomenclature'),
            'service_codes': fields.related('product_id',
                                            'service_codes',
                                            type="many2one",
                                            relation="account.cee.service.codes",
                                            readonly=True,
                                            string='Combined Nomenclature for Services'),
            'unit_net_mass': fields.related('product_id',
                                            'net_mass',
                                            type="float",
                                            relation="product.product",
                                            readonly=True,
                                            string='Unit Net Mass'),
            'total_net_mass': fields.function(_get_tot_net_mass,
                                              type="float",
                                              readonly=True,
                                              string='Total Net Mass'),
            'unit_statistical_value': fields.related('product_id',
                                                     'statistical_value',
                                                     type="float",
                                                     relation="product.product",
                                                     readonly=True,
                                                     string='Unit Statistical Value'),
            'total_statistical_value': fields.function(_get_tot_stat,
                                                       type="float",
                                                       readonly=True,
                                                       string='Total Statistical Value'),
            'uom_secondary': fields.related('product_id',
                                            'uom_secondary',
                                            type="many2one",
                                            relation="product.uom",
                                            readonly=True,
                                            string='Secondary UOM'),
            'qty_uom_secondary': fields.function(_get_qty_second_uom,
                                                 type="float",
                                                 readonly=True,
                                                 string='Quantity in Secondary UOM'),
            # Paese di provenienza
            'country_provenance': fields.many2one('res.country',
                                                  'Provenance Country'),
            # Paese di origine
            'country_origin': fields.many2one('res.country',
                                              'Origin Country'),
            # Provincia destinazione
            'province_destination': fields.many2one('res.province',
                                                    'Province destination'),
            # Modo trasporto - alfa 1
            'way_of_freight': fields.many2one('account.cee.way.of.freight',
                                              'Way of freight'),
            'is_intracee': fields.function(_is_intracee,
                                           type="boolean",
                                           string='Is Intracee'),

            'flow_number': fields.integer('Flusso Intrastat',
                                          size=6,
                                          readonly=True)
        }

    def _default_country_provenance(self, cr, uid, context=None):
        if ('partner_id' in context
                and 'fiscal_position' in context
                and self.check_intracee(cr, uid, context['fiscal_position'], context=context)):
            if context['partner_id']:
                t_partner_id = context['partner_id']
                t_partner_obj = self.pool.get('res.partner')
                if t_partner_id:
                    t_partner_data = t_partner_obj.browse(cr, uid, t_partner_id)
                    if t_partner_data.country_provenance:
                        return t_partner_data.country_provenance.id
        return None

    def _default_country_origin(self, cr, uid, context=None):
        if ('partner_id' in context
                and 'fiscal_position' in context
                and self.check_intracee(cr, uid, context['fiscal_position'], context=context)):
            if context['partner_id']:
                t_partner_id = context['partner_id']
                t_partner_obj = self.pool.get('res.partner')
                if t_partner_id:
                    t_partner_data = t_partner_obj.browse(cr, uid, t_partner_id)
                    if t_partner_data.country_origin:
                        return t_partner_data.country_origin.id
        return None

    def _default_province_destination(self, cr, uid, context=None):
        if ('company_id' in context
                and 'fiscal_position' in context
                and context['fiscal_position']
                and self.check_intracee(cr, uid, context['fiscal_position'], context=context)):
            if context['company_id']:
                t_company_id = context['company_id']
                t_company_obj = self.pool.get('res.company')
                if t_company_id:
                    t_company_data = t_company_obj.browse(cr, uid, t_company_id)
                    if t_company_data.province_destination:
                        return t_company_data.province_destination.id
        return None

    def _default_way_of_freight(self, cr, uid, context=None):
        if ('partner_id' in context
                and 'fiscal_position' in context
                and self.check_intracee(cr, uid, context['fiscal_position'], context=context)):
            if context['partner_id']:
                t_partner_id = context['partner_id']
                t_partner_obj = self.pool.get('res.partner')
                if t_partner_id:
                    t_partner_data = t_partner_obj.browse(cr, uid, t_partner_id)
                    if t_partner_data.way_of_freight:
                        return t_partner_data.way_of_freight.id
        return None

    def _default_is_intracee(self, cr, uid, context=None):
        if ('fiscal_position' in context
                and self.check_intracee(cr, uid, context['fiscal_position'], context=context)):
            return True
        return False

    _defaults = {
        'country_provenance': _default_country_provenance,
        'country_origin': _default_country_origin,
        'province_destination': _default_province_destination,
        'way_of_freight': _default_way_of_freight,
        'is_intracee': _default_is_intracee,
    }
