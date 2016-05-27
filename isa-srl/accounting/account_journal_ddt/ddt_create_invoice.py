# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class ddt_create_invoice(models.TransientModel):

    _inherit = ['ddt.create.invoice']

    automatic_setting_journal = fields.Boolean(
        string='Impostazione automatica sezionale',
        required=False,
        readonly=False,
        index=False,
        default=True,
        help="Permette di imputare automaticamente il sezionale in base al picking type"
    )

    @api.multi
    def create_invoice(self):
        '''
        La funzione reperisce gli active_ids e se specificato il flag di impostazione automatica del sezionale
        ricerca il sezionale da impostare e verifica se per ogni picking type è stato impostato il sezionale di
        default
        '''
        new_context = self.env.context.copy()
        # Se non è stato impostato il reperimento automatico del sezionale eseguo la funzione normalmente
        if not self.automatic_setting_journal:
            return super(ddt_create_invoice, self.with_context(new_context)).create_invoice()

        active_ids = self.env.context['active_ids']
        # Reperisco i ddt
        stock_ddts = self.env['stock.ddt'].browse(active_ids)
        # Reperisco i picking type
        picking_types = stock_ddts.mapped('picking_ids').mapped('picking_type_id')
        if any(not picking_type.ddt_default_journal for picking_type in picking_types):
            raise Warning("""Per alcuni picking type non è stato impostato il Sezionale di default DDT.
                Per fatturare utilizzando la funzione Impostazione automatica sezionale è necessario che ogni
                picking type abbia valorizzato il Sezionale di default DDT.""")
        
        # Raggruppo i picking in base al journal_id dei picking_type relativi ai picking contenuti
        invoice_ids = []
        t_ddt_dict = {}  
        for stock_ddt in stock_ddts:
            
            t_picking_type = (stock_ddt.picking_ids and stock_ddt.picking_ids[0] and stock_ddt.picking_ids[0].picking_type_id) or 0
            key = (t_picking_type.ddt_default_journal.id,)

            if key not in t_ddt_dict:
                t_ddt_dict[key] = []
            t_ddt_dict[key].append(stock_ddt.id)      

        # Per ogni raggruppamento di DDT, chiamo la super passando il relativo journal_id
        for key in t_ddt_dict:            
            new_context.update({'active_ids': t_ddt_dict[key]})
            self.journal_id = key[0]
            result = None
            result = super(ddt_create_invoice, self.with_context(new_context)).create_invoice()
            # Dal result devo intercettare il domain per reperire l'id della fattura creata.
            domain = result.get('domain', False)[0]
            useless_key, useless_operator, value = domain
            # Unisco i risultati delle liste
            invoice_ids = list(set(invoice_ids) | set(value))
        # Riporto il risultato###

        mod_obj = self.env['ir.model.data']

        search_view_res = mod_obj.get_object_reference('account', 'view_account_invoice_filter')
        search_view_id = search_view_res and search_view_res[1] or False

        form_view_res = mod_obj.get_object_reference('account', 'invoice_form')
        form_view_id = form_view_res and form_view_res[1] or False

        return  {
            'domain': [('id', 'in', invoice_ids)],
            'name': 'Fatture da DDT',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'views': [(False, 'tree'), (form_view_id, 'form')],
            'search_view_id': search_view_id,
        }

