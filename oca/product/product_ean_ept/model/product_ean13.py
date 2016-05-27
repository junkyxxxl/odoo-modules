# -*- coding: utf-8 -*-

from openerp import models, fields,api,_
from datetime import datetime
from openerp.exceptions import Warning
from openerp.addons.product import product as product
import string 

class product_ean13(models.Model):
    _name = 'product.ean13'
    _description = "List of EAN13 for a product."
    _order = 'sequence'
    
    name = fields.Char('EAN Number', copy=False)
    product_id = fields.Many2one('product.product',string='Product',required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence')
    by_supplier = fields.Boolean('Provided By Supplier',default=False,help="This is useful to know the barcode is of supplier or not")
    supplier_id = fields.Many2one('res.partner',string='Supplier Name')
    type = fields.Selection(string='EAN Type',selection=[('EAN8', 'EAN8'),('EAN13', 'EAN13'),('EAN128', 'EAN128'),('CODE128', 'CODE128'),('PHARMACODE', 'PHARMACODE')],default='EAN13')
    quantity = fields.Integer('Quantity', default=1)
    created_by = fields.Many2one('res.users',string='Created By',readonly=True)
    created_date = fields.Datetime('Created Date')
    modified_date = fields.Datetime('Modified Date')
    auto_generated = fields.Boolean(string='Auto generated', readonly=True, copy=False, default=False)
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'EAN number already exist. EAN Number must be Unique.!'),
    ]
        
    @api.one
    @api.constrains('name')
    def _check_ean_key(self):
        if self.by_supplier:
            res = product.check_ean(string.zfill(self.name,13))
            if not res:
                raise Warning(_('Error: Invalid ean code.'))
        
    @api.model
    def create(self, vals):
        """Create ean13 with a sequence higher than all
        other products when it is not specified"""
        if not vals.get('sequence') and vals.get('product_id'):
            ean13s = self.search([('product_id', '=', vals['product_id'])])
            vals['sequence'] = 1
            if ean13s:
                vals['sequence'] = max([ean.sequence for ean in ean13s]) + 1
                
        vals['created_by'] = self.env.uid
        vals['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vals['modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return super(product_ean13, self).create(vals)
    
    @api.multi
    def write(self,vals):
        vals['modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        res = super(product_ean13,self).write(vals)
        return res
    
    @api.multi
    @api.depends('name', 'product_id')
    def name_get(self):
        res = []
        for record in self:
            if record.product_id.default_code:
                descr = ("[%s] %s") % (record.product_id.default_code, record.product_id.name)
            else:
                descr = ("%s") % (record.product_id.name)
            res.append((record.id, descr))
        return res    
    
    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        if not args:
            args = []
        args = args[:]
        #Provo a ricercare per nome prodotto o riferimento interno
        products = self.env['product.product'].search(['|',('name',operator,name),('default_code',operator,name)])
        product_ids = [product.id for product in products]
        records = self.search(['|',('name', operator, name),'&',('product_id','in',product_ids),('auto_generated','=',True)] + args,
                              limit=limit)
        return records.name_get()