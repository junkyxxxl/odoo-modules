from openerp import fields, models, api
import time

class hr_report(models.TransientModel):
    _name = 'hr.report'
    _description = 'Print Monthly Holidays Report'

    @api.model
    def _get_selected_employee(self):
        selected = self.env['hr.employee'].search([('id', '=', self.env.context.get('active_ids'))])
        return selected

    month= fields.Selection([(1, 'January'),
                             (2, 'February'),
                             (3, 'March'),
                             (4, 'April'),
                             (5, 'May'),
                             (6, 'June'),
                             (7, 'July'),
                             (8, 'August'),
                             (9, 'September'),
                             (10, 'October'),
                             (11, 'November'),
                             (12, 'December')],
                            'Month', required=True, default =lambda *a: time.gmtime()[1])

    year= fields.Integer('Year', required=True, default =lambda *a: time.gmtime()[0])
    print_holidays= fields.Boolean('Report Permessi',default=True)
    print_attendances= fields.Boolean('Report Presenze Effettive',default=True)
    print_overtime= fields.Boolean('Report Straordinari',default=True)
    employee = fields.Many2many('hr.employee',default = _get_selected_employee)

    def _build_contexts(self, data):
        result = {}
        result['month'] ='month' in data['form'] and data['form']['month'] or False
        result['year'] = 'year' in data['form'] and data['form']['year'] or False
        return result

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['month', 'year','employee','print_holidays','print_attendances','print_overtime'])[0]
        used_context = self._build_contexts(data)
        data['form']['used_context'] = dict(used_context, lang=self.env.context.get('lang', 'en_US'))
        return self._print_report(data)

    def _print_report(self,data):
        return self.env['report'].get_action(self,'hr_report.print_attendance',data = data)