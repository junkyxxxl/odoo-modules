from openerp import models, fields, api
from datetime import datetime
import datetime

class flag(models.TransientModel):
    _inherit = 'hr.config.settings'

    @api.model
    def get_manage_working_hour(self):
        stock_config_obj = self.env['hr.config.settings'].search([], limit=1, order="id DESC")
        return stock_config_obj.manage_working_hour

    module_hr_holidays_working_hour = fields.Boolean('Gestisci i permessi in ore')