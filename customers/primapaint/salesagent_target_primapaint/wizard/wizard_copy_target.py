# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning, ValidationError


class wizard_copy_salesagent_target(models.TransientModel):
    """Wizard to copy target"""

    _name = "wizard.copy.salesagent.target"
    _description = "Copy salesagent target"

    salesagent_target_id = fields.Many2one(
        string='Salesagent target id',
        required=True,
        readonly=True,
        comodel_name='salesagent.target',
        ondelete='cascade',
    )

    salesagent_from_id = fields.Many2one(
        'res.partner',
        string="Salesagent",
        domain="[('salesagent', '=', True)]",
        required=True,
        readonly=True,
        ondelete='cascade',
    )

    categ_from_id = fields.Many2one(
        'product.category',
        string="Product category",
        required=False,
        ondelete='cascade',
        domain="[('parent_id','!=', False),('child_id', '=', False)]"
    )

    year_from_id = fields.Many2one(
        'account.fiscalyear',
        string="Year",
        required=True,
        ondelete='cascade',
    )

    salesagent_to_id = fields.Many2one(
        'res.partner',
        string="Salesagent",
        domain="[('salesagent', '=', True)]",
        required=True,
        ondelete='cascade',
    )

    categ_to_id = fields.Many2one(
        'product.category',
        string="Product category",
        ondelete='cascade',
        domain="[('parent_id','!=', False),('child_id', '=', False)]"
    )

    year_to_id = fields.Many2one(
        'account.fiscalyear',
        string="Year",
        required=True,
        ondelete='cascade',
    )

    target_deviation = fields.Float(
        string='Target deviation',
        required=False,
        default=0.0,
        digits=dp.get_precision('Salesagent target'),
    )

    @api.one
    def copy_target(self):
        # Eseguo i controlli
        # I dati da cui copiare e su cui copiare devono essere diversi.
        if (
            self.salesagent_from_id == self.salesagent_to_id and
            self.categ_from_id and
            self.categ_from_id == self.categ_to_id and
            self.year_from_id == self.year_to_id
        ):
            raise Warning(_("Data from copy and to copy cannot be equal."))
        # Divido i due casi, se specificata la categoria oppure non è specificata
        # e vuol dire che le devo copiare tutte
        new_target = []
        if self.categ_from_id:
            target_new_id = self._copy_only_one_category(self.categ_to_id)
            new_target.append(target_new_id)
        else:
            # Passo categoria per categoria ed eseguo la copia, se la categoria
            # già non esiste.
            for category in self.salesagent_target_id.categ_id.parent_id.child_id:
                # Verifico se già esiste un record per agente/anno/categoria
                target = self.env['salesagent.target'].search([
                    ('categ_id', '=', category.id),
                    ('salesagent_id', '=', self.salesagent_to_id.id),
                    ('year_id', '=', self.year_to_id.id)
                ])
                if not target.exists():
                    self._copy_only_one_category(category)

    def _copy_only_one_category(self, category):
        # Accedo al target di destinazione da cui copiare
        target_obj = self.salesagent_target_id
        # Copio il record modificando i dati necessari
        target_copy = target_obj.copy({
            'salesagent_id': self.salesagent_to_id.id,
            'year_id': self.year_to_id.id,
            'categ_id': category.id
        })
        target_line_copy = target_obj.salesagent_target_line_ids.copy({
            'salesagent_target_id': target_copy.id
        })
        # se non è stato specificato lo scostamento del target ho ultimato
        # la copia.
        if not self.target_deviation or self.target_deviation == 0:
            return target_copy.id
        rate = self.target_deviation / 100
        for target_line in target_line_copy:
            target_line.target = target_line.target * (1+rate)
        return target_copy.id
