
import time

from openerp import fields, models, api


ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'province', 'region')


class Partner(models.Model):
    # This OpenERP object inherits from res.partner

    _inherit = 'res.partner'

    @api.model
    def create(self, vals):

        # controlla se non e' un'azienda
        # ed eredita l'indirizzo
        # if not vals['is_company']:
        # vals['use_parent_address']= True

        if 'is_company' not in vals or not vals['is_company']:
            vals['use_parent_address'] = True

        # per mettere di default come commerciale l'utente che crea la scheda cliente:
        # se non e' stato specificato il commerciale controllo se fra i gruppi cui appartiene l'utente 
        # ce n'e' almeno uno che appartiene alla categoria commerciale
        if 'user_id' not in vals or not vals['user_id']:
            utente = self.env['res.users'].browse(self._uid)
            for gruppo in utente.groups_id:

                # if gruppo.category_id.name == "Sales": 
                # quasi tutti gli utenti sono in uno dei gruppi vendita, quindi occorre un test diverso per individuare
                # i commerciali, ad esempio quelli che appartengono al gruppo BEC - commerciali:
                if gruppo.name == 'Own Salesperson ONLY':
                    vals['user_id'] = utente.id
                    break

        # poi richiamo la funzione standard di creazione
        return super(Partner, self).create(vals)

    @api.multi
    def write(self, vals):

        # aggiorna 'utente' e 'data' salvataggio
        vals['bec_modify_date'] = fields.Datetime.now()
        vals['bec_modify_user'] = self._uid

        return super(Partner, self).write(vals)

    def onchange_is_modify(self, cr, uid, ids, bec_is_modify):

        value = {}
        if bec_is_modify:
            value['bec_state'] = 'modified'
            value['bec_is_modify_date'] = fields.Datetime.now()  # time.strftime('%Y-%m-%d')
        else:
            value['bec_state'] = 'confirmed'
            value['bec_is_modify_date'] = False
            value['bec_is_modify_why'] = ''

        return {'value': value}

    bec_comment_fm = fields.Html('Note FM', help='Automatically sanitized HTML contents')

    bec_is_modify = fields.Boolean('Modified', required=False)
    bec_send_magazine = fields.Boolean('Send Magazine', required=False)
    bec_send_data_comparison = fields.Boolean('Send Data Comparison', required=False)

    bec_is_modify_why = fields.Char('Change Why', size=128, help='Max 128 char')

    bec_is_modify_date = fields.Date('Change Date', help='Date modified record.')

    bec_state = fields.Selection([('confirmed', 'Confirmed'),
                                  ('modified', 'Modified'),
                                  ('cancel', 'Cancelled'),
                                  ('delete', 'Delete')],
                                 string='Status',
                                 default='confirmed')

    bec_create_user = fields.Many2one('res.users', 'User Creation', readonly=True, help='The internal user who entered the record.')
    bec_modify_user = fields.Many2one('res.users', 'User Modification', readonly=True, help='The internal user has modified the record.')

    bec_create_date = fields.Datetime('Creation Date', readonly=True, help='Date added record.')
    bec_modify_date = fields.Datetime('Modified Date', readonly=True, help='Date modified the record.')

    bec_code_province = fields.Char(related='province.code', size=2, comodel_name="res.province", string="Province Code", readonly=True, help='The province code in two chars.', store=True)

    _defaults ={
        'bec_create_user': lambda self, cr, uid, context: uid,
        'bec_create_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
