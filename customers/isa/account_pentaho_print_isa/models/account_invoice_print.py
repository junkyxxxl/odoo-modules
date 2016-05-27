# -*- coding: utf-8 -*-
from openerp import models, fields, api


class account_invoice_print(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def invoice_print(self):
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'account.report_invoice_pentaho')    
    

class sale_order_print(models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def print_quotation(self):   
        assert len(self) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow('quotation_sent')
        return self.env['report'].get_action(self, 'sale.order.pentaho')
