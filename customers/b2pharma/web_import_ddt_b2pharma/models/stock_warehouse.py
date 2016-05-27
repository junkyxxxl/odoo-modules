# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import Warning


class stock_warehouse(models.Model):

    _inherit = ['stock.warehouse']

    document_type_sample_id = fields.Many2one(
        string='Tipo documento materiale campione',
        required=False,
        help='''Tipo documento da impostare automaticamete durante la procedura di importazione ddt per materiali
        campione''',
        comodel_name='sale.document.type',
    )

    @api.one
    @api.constrains('document_type_sample_id')
    def _check_document_type_format(self):
        '''
        Eseguo un controllo per accertarmi che se è stato specificato il tipo documento
        da imputare all'ordine di vendita per le importazioni ddt dei campioni, la rotta di tale
        tipo documento deve:
         - essere sempre presente
         - Avere una sola regola PULL e nessuna regola PUSH
         - All'interno della regola PULL lo stato fatturazione deve essere non applicabile
          (i movimenti di importazione di materiali campione non possono essere fatturati)
        '''
        if self.document_type_sample_id:
            # Deve sempre essere presente la rotta
            if not self.document_type_sample_id.route_id:
                raise Warning("Per il tipo documento materiale campione deve essere presente una rotta.")
            route = self.document_type_sample_id.route_id
            # La rotta non può avere regole di tipo PUSH
            if route.push_ids.exists():
                raise Warning(
                    '''La rotta associata ad un tipo documento per materiale campione non può contenere regole di tipo PUSH
                    ''')
            # La rotta deve contenere solo una regola di tipo  PULL
            if len(route.pull_ids) != 1:
                raise Warning(
                    '''La rotta associata ad un tipo documento per materiale campione deve contenere esattamente una sola
                    regola di tipo PULL
                    ''')
            # La regola di tipo pull deve avere stato fatturazione uguale a non fatturare
            pull_rule = route.pull_ids[0]
            if pull_rule.invoice_state != 'none':
                raise Warning('''La rotta associata ad un tipo documento per materiale campione deve contenere esattamente una sola
                    regola di tipo PULL con stato fattura uguale a "Non applicabile"
                    ''')
