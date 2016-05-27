# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv

class sale_report(osv.osv):

    _inherit = 'sale.report'

    _columns = {
        'region': fields.many2one('res.region', 'Regione cliente', readonly=True),
        'province': fields.many2one('res.province', 'Provincia cliente', readonly=True),
        'destination_region': fields.many2one('res.region', 'Regione destinazione merce', readonly=True),
        'destination_province': fields.many2one('res.province', 'Provincia destinazione merce', readonly=True),
        'price_total_discount': fields.float('Prezzo Totale Scontato', readonly=True)
    }
    
    #Eseguo l'overriding dei metodi presenti nella classe sale_report del modulo sale, in cui i dati per costruire la tabella
    #in odoo sotto: Reportistica->Analisi delle vendite, vengono presi tramite Sql;
    #con la super(nome_tabella).nome_metodo_da_richiamare(), faccio un append delle cose da aggiungere alla query
    def _select(self):
        str_select = super(sale_report,self)._select()
        str_select += """ ,rp.region, rp.province, rp1.region as destination_region, rp1.province as destination_province, 
                           sum(l.product_uom_qty * cr.rate * l.price_unit * (100.0-l.discount) / 100.0) - 
                              (s.global_discount_percentual * (
                                  sum(l.product_uom_qty * cr.rate * l.price_unit * (100.0-l.discount) / 100.0))
                              ) as price_total_discount
                      """
        return str_select

    def _from(self):
        str_from = super(sale_report,self)._from()
        str_from += """ left join res_partner rp on (rp.id = s.partner_id) 
                        left join res_partner rp1 on (rp1.id = s.partner_shipping_id)
                    """
        return str_from        
    
    def _group_by(self):
        str_group = super(sale_report,self)._group_by()
        str_group += ' ,rp.region, rp.province, rp1.region, rp1.province, s.global_discount_percentual'
        return str_group          