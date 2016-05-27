# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import time
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning
    
class account_commission_line(models.Model):
    _name = "account.commission.line"
    _description = "Commission Line"

    @api.one
    @api.depends('line_agent_id', 'line_agent_id.invoice_id.state', 'commission_mode')
    def _get_state(self):
        if self.line_agent_id:
            if self.line_agent_id.invoice_id.state == 'paid':
                self.state = 'paid'
            else:
                self.state = 'invoiced'
        else:
            if (self.commission_mode == 'invoiced' and self.line_src_id) or (self.commission_mode == 'paid' and self.line_src_id and self.line_src_id.invoice_id.state == 'paid'):
                self.state = 'matured'
            else:
                self.state = 'computed'            
    
    line_src_id = fields.Many2one('account.invoice.line', string="Origin Line", )
    line_agent_id = fields.Many2one('account.invoice.line', string="Inoice Line", )
    salesagent_id = fields.Many2one('res.partner', string="Salesagent", )

    base_untaxed = fields.Float(string="Untaxed Base", digits_compute= dp.get_precision('Account'),)
    amount_commission = fields.Float(string="Amount Commission", digits_compute= dp.get_precision('Account'),)

    commission_mode = fields.Selection([('invoiced','Invoiced'),('paid','Paid')], string="Commission Mode", help="Defines the maturity conditions for commissions", default=None, )        
    state = fields.Selection([('computed','Computed'),('matured','Matured'),('invoiced','Invoiced'),('paid','Paid')], string="State", default='computed', compute="_get_state", store=True, )
    
    invoice_src_id = fields.Many2one('account.invoice', string="Origin Invoice", store=True, related="line_src_id.invoice_id", )
    fiscalyear_id = fields.Many2one('account.fiscalyear', string="Fiscal Year", store=True, related="line_src_id.invoice_id.period_id.fiscalyear_id", )
    partner_id = fields.Many2one('res.partner', string="Partner", store=True, related="line_src_id.invoice_id.partner_id", )
    invoice_agent_id = fields.Many2one('account.invoice', string="Invoice", store=True, related="line_agent_id.invoice_id", )
    move_id = fields.Many2one('account.move', string="Account Move", store=True, related="line_agent_id.invoice_id.move_id")        
    invoice_src_type = fields.Selection([('out_invoice','Customer Invoice'),('in_invoice','Supplier Invoice'),('out_refund','Customer Refund'),('in_refund','Supplier Refund')], string="Origin Invoice Type", store=True, related="line_src_id.invoice_id.type", )    
    invoice_date = fields.Date(string="Invoice Date", store=True, related="line_src_id.invoice_id.date_invoice", )
    salesagent_code = fields.Char(string="Salesagent Code", store=True, related="salesagent_id.salesagent_code", )
    
    who_did_the_order = fields.Many2one('res.users', string="Sold By", store=True, related="line_src_id.invoice_id.user_id", )
    
    @api.one
    def unlink(self):
        if self.state in ['invoiced','paid']:
            raise Warning(_("It's not possible to delete commission line already invoiced or paid"))
        return super(account_commission_line,self).unlink() 