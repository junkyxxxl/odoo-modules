# -*- coding: utf-8 -*-
from openerp import models
import re


class ModelName(models.Model):

    _inherit = ['stock.move']

    def sanitize_description(self):
        # Tolgo il codice da dentro le parentesi perchè viene stampato a parte.
        # Il codice viene ridefinito dalla name_get di un altro modulo. Questa
        # pulizia mi serve solo per il report.
        return re.sub('[[].+?[]]', '', self.name)
