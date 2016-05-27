# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class salesagent_target(models.Model):

    _name = "salesagent.target"
    _description = "Salesagent target"

    name = fields.Text(
        string='Name',
        compute=lambda self: self._compute_name()
    )
    salesagent_id = fields.Many2one(
        'res.partner',
        string="Salesagent",
        domain="[('salesagent', '=', True)]",
        required=True
    )
    categ_id = fields.Many2one(
        'product.category',
        string="Product category",
        required=True,
        domain="[('parent_id','!=', False),('child_id', '=', False)]"
    )
    year_id = fields.Many2one(
        'account.fiscalyear',
        string="Year",
        required=True
    )
    threshold = fields.Float(
        string='Threshold awards',
        required=True,
        default=0.0,
        digits=dp.get_precision('Salesagent target'),
        copy=False
    )
    salesagent_target_line_ids = fields.One2many(
        string='Salesagent target line',
        comodel_name='salesagent.target.line',
        inverse_name='salesagent_target_id',
    )

    _sql_constraints = [
        ('target_unique', 'unique(salesagent_id, categ_id, year_id)', _('Target already exists for salesagent/category/year'))
    ]

    @api.one
    @api.depends('salesagent_id', 'categ_id', 'year_id')
    def _compute_name(self):
        self.name = "%s / %s / %s" % (self.salesagent_id.name, self.categ_id.name, self.year_id.name)

    @api.model
    def create(self, vals):
        salesagent_target_obj = super(salesagent_target, self).create(vals)
        if salesagent_target:
            self.load_months()
        return salesagent_target_obj

    @api.one
    def load_months(self):
        months = []
        for i in range(1, 13):
                month = str(i).zfill(2)
                line_month = self.salesagent_target_line_ids.filtered(lambda m: m.month == month)
                if not line_month.exists():
                    target_line_value = {
                        'target': 0,
                        'month': month
                    }
                    months.append((0, 0, target_line_value))
        self.update({'salesagent_target_line_ids': months})
        return self


class salesagent_target_line(models.Model):

    _name = "salesagent.target.line"
    _description = "Salesagent target line"
    _order = "month"

    salesagent_target_id = fields.Many2one(
        comodel_name='salesagent.target',
        string="Salesagent Target",
        ondelete='cascade',
        readonly=True,
    )
    month = fields.Selection(
        string='Month',
        required=True,
        readonly=False,
        selection=[
            ('01', _('January')),
            ('02', _('February')),
            ('03', _('March')),
            ('04', _('April')),
            ('05', _('May')),
            ('06', _('June')),
            ('07', _('July')),
            ('08', _('August')),
            ('09', _('September')),
            ('10', _('October')),
            ('11', _('November')),
            ('12', _('December')),
        ]
    )
    target = fields.Float(
        string='Target',
        required=True,
        default=0.0,
        digits=dp.get_precision('Salesagent target'),
    )

    _sql_constraints = [
        ('month_unique', 'unique(month, salesagent_target_id)', _('Duplicated month'))
    ]
