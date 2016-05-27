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

class sale_report_montecristo(osv.osv):
    _inherit = "sale.report"


    _columns = {
        'template_id': fields.many2one('product.template', 'Template', readonly=True),
        'template_code': fields.char('Riferimento interno', readonly=True),
        'size_id': fields.many2one('product.attribute.value', 'Taglia', readonly=True),
        'color_id': fields.many2one('product.attribute.value', 'Colore', readonly=True),
        'salesagent_id': fields.many2one('res.partner', 'Agente', readonly=True),
        'delivery_date': fields.date("Data di consegna"),
        'payment_term': fields.many2one('account.payment.term','Tipo Pagamento'),
        'season': fields.many2one('res.family','Stagionalità'),
        
        'family': fields.many2one('res.family','Famiglia'),
        'subfamily': fields.many2one('res.family','Sottofamiglia'),
        'subgroup': fields.many2one('res.family','Sottogruppo'),
        'composition': fields.many2one('res.family','Composizione'),
        'origin': fields.many2one('res.family','Origine')
        
    }
    _order = 'date desc'

    def _select(self):
        select_str = super(sale_report_montecristo,self)._select()
        select_str = select_str.replace('sum(l.product_uom_qty * cr.rate * l.price_unit * (100.0-l.discount) / 100.0) as price_total,','sum((l.product_uom_qty * cr.rate * l.price_unit * (100.0-l.discount) / 100.0) * (1 - s.global_discount_percentual)) as price_total,')       
        select_str = select_str + """,
                    s.salesagent_id as salesagent_id,
                    s.payment_term as payment_term,
                    t.id as template_id,
                    t.tmpl_default_code as template_code,
                    s.delivery_date as delivery_date,
                    s.season as season,
                    t.famiglia as family,
                    t.sottofamiglia as subfamily,
                    t.sottogruppo as subgroup,
                    t.composizione as composition,
                    t.origine as origin,
                    (
                    SELECT val.id as "size_id"
                    FROM product_attribute_value AS val, product_attribute AS att
                    WHERE val.id IN 
                        (
                        SELECT pd_rel.att_id
                        FROM product_attribute_value_product_product_rel AS pd_rel
                        WHERE pd_rel.prod_id = product_id 
                        ) AND att.position = 'column' AND att.id = val.attribute_id
                    LIMIT 1
                    ),
                    (
                    SELECT val.id as "color_id"
                    FROM product_attribute_value AS val, product_attribute AS att
                    WHERE val.id IN 
                        (
                        SELECT pd_rel.att_id
                        FROM product_attribute_value_product_product_rel AS pd_rel
                        WHERE pd_rel.prod_id = product_id 
                        ) AND att.position = 'row' AND att.id = val.attribute_id
                    LIMIT 1
                    )
        """
        return select_str

    def _group_by(self):
        group_by_str = super(sale_report_montecristo,self)._group_by()
        group_by_str = group_by_str + """,
                    s.salesagent_id,
                    s.payment_term,
                    t.id,
                    t.tmpl_default_code,
                    s.delivery_date,
                    s.season,
                    t.famiglia,
                    t.sottofamiglia,
                    t.sottogruppo,
                    t.composizione,
                    t.origine,
                    size_id,
                    color_id
        """
        return group_by_str


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
