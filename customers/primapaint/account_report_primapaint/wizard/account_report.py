from openerp import fields, models, api

class account_report(models.TransientModel):
    _name = 'account.report'


    @api.model
    def _get_fiscal_year(self):
        #Reperisco tutti gli anni fiscali
        fiscal_year_obj = self.env['account.fiscalyear'].search([])
        if fiscal_year_obj:
            return [(year.code, year.name) for year in fiscal_year_obj]
        else:
            return [(None, '')]


    @api.model
    def _get_selected_salesagent(self):
        #Prendo gli agenti che sono stati selezionati da tree view
        selected = self.env['res.partner'].search([('id', 'in', self.env.context.get('active_ids'))])
        return selected

    category = fields.Many2one('product.category', string='Categoria', required=True)
    budget_year = fields.Selection('_get_fiscal_year', string='Anno del budget', default=lambda self: self.env['account.fiscalyear'].search([])[0].code, required=True)
    salesagent = fields.Many2many('res.partner', default=_get_selected_salesagent)


    def _build_contexts(self, data):
        result = {}
        result['category'] ='category' in data['form'] and data['form']['category'] or False
        result['budget_year'] = 'budget_year' in data['form'] and data['form']['budget_year'] or False
        return result

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['category', 'budget_year','salesagent'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)

    def _print_report(self,data):
        return self.env['report'].get_action(self,'account_report_primapaint.print_budget',data = data)



