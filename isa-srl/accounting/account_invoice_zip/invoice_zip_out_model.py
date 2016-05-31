# -*- coding: utf-8 -*-
from openerp import fields, models, api

class invoice_zip_model(models.Model):
    _name = 'invoice.zip'

    filedata = fields.Binary('File Zip', filters='*.zip')
    filename = fields.Char('File Name')
    type = fields.Text()
    element = fields.Text()
