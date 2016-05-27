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


class product_template_intracee(orm.Model):

    _inherit = "product.template"

    _columns = {
            'tmpl_combined_nomenclature': fields.many2one('account.cee.combined.nomenclature', 'Combined Nomenclature'),
            'tmpl_service_codes': fields.many2one('account.cee.service.codes', 'Nomenclatura combinata per servizi'),
            'tmpl_net_mass': fields.float('Net Mass'),
            'tmpl_statistical_value': fields.float('Statistical Value'),
            'tmpl_uom_secondary': fields.many2one('product.uom', 'Secondary Unit of Measure'),
            'tmpl_uom_secondary_coeff': fields.float('Secondary UoM Coefficient'),                  
    }

    def create_variant_ids(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        tmpl_combined_nomenclature = self.browse(cr,uid,ids[0]).tmpl_combined_nomenclature
        if tmpl_combined_nomenclature:
            context.update({'tmpl_combined_nomenclature':tmpl_combined_nomenclature.id})

        tmpl_service_codes = self.browse(cr,uid,ids[0]).tmpl_service_codes            
        if tmpl_service_codes:
            context.update({'tmpl_service_codes':tmpl_service_codes.id})

        tmpl_net_mass = self.browse(cr,uid,ids[0]).tmpl_net_mass            
        if tmpl_net_mass:
            context.update({'tmpl_net_mass':tmpl_net_mass})                

        tmpl_statistical_value = self.browse(cr,uid,ids[0]).tmpl_statistical_value                    
        if tmpl_statistical_value:
            context.update({'tmpl_statistical_value':tmpl_statistical_value})

        tmpl_uom_secondary = self.browse(cr,uid,ids[0]).tmpl_uom_secondary            
        if tmpl_uom_secondary:
            context.update({'tmpl_uom_secondary':tmpl_uom_secondary.id})    

        tmpl_uom_secondary_coeff = self.browse(cr,uid,ids[0]).tmpl_uom_secondary_coeff            
        if tmpl_uom_secondary_coeff:
            context.update({'tmpl_uom_secondary_coeff':tmpl_uom_secondary_coeff})                  

        return super(product_template_intracee,self).create_variant_ids(cr,uid,ids,context)
