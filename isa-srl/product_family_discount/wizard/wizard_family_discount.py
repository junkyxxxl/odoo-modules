# -*- coding: utf-8 -*-
from openerp import fields, models, api, _

class wizard_family_discount(models.TransientModel):
    _name = 'wizard.family.discount'

    discount = fields.Float()
    check = fields.Boolean()
    category = fields.Many2one('category.partner',string='Categoria Cliente',store=True,required=True,)
    type = fields.Many2one('product.family',domain=[('type','=','family')],required=True)

    @api.multi
    def set_discount(self):
        partner = self.env['res.partner'].search([('partner_category', '=', self.category.id)])
        family_discount_object = self.env['product.family.discount']
        if self.check != True: #se l'utente non vuole sovrascrivere
            for p in partner:
                    test = self.env['product.family.discount'].search([('partner_id','=',p.id),('family_id','=',self.type._ids[0])])
                    if test.ids.__len__() == 0: #se lo sconto sulla famiglia per il cliente non esiste allora viene creato, altrimenti viene lasciato invariato
                        vals = {'family_id': self.type._ids[0],
                                'discount': self.discount,
                                'partner_id':p.id
                                }
                        family_discount_object.create(vals)
        else:
            for p in partner:
                    test = self.env['product.family.discount'].search([('partner_id','=',p.id),('family_id','=',self.type._ids[0])])
                    if test.ids.__len__() == 0: #se non esiste lo sconto lo crei
                        vals = {'family_id': self.type._ids[0],
                                'discount': self.discount,
                                'partner_id': p.id
                                }
                        family_discount_object.create(vals)
                    else:
                        test.unlink()
                        vals = {'family_id': self.type._ids[0],
                                'discount': self.discount,
                                'partner_id': p.id
                                }
                        family_discount_object.create(vals)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(self._cr, self._uid, 'base', 'view_partner_tree')
        view_id = result and result[1] or False

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "views": [[False, "kanban"], [False, "tree"], [False, "form"]],
            "context": {"search_default_customer":1,
                        "search_default_partner_category": self.category.id}
        }
