from openerp import models, fields, api
from datetime import datetime
import datetime

class flag(models.TransientModel):
    _inherit = 'hr.config.settings'

    module_hr_holidays_working_hour = fields.Boolean('Gestisci i permessi in ore', help="Installa il modulo hr_holidays_working_hour")