# -*- coding: utf-8 -*-
from openerp import models, fields, api
from ast import literal_eval

class auth_signup_sale(models.Model):
    
    _inherit='res.users'
    
    @api.cr_uid_context
    def _signup_create_user(self, cr, uid, values, context=None):
        """ create a new user from the template user """
        ir_config_parameter = self.pool.get('ir.config_parameter')
        template_user_id = literal_eval(ir_config_parameter.get_param(cr, uid, 'auth_signup.template_user_id', 'False'))
        assert template_user_id and self.exists(cr, uid, template_user_id, context=context), 'Signup: invalid template user'
        template_user = self.browse(cr, uid, template_user_id, context)
        #dal template user reperisco la posizione fiscale ed il listino di vendita
        if template_user.property_account_position:
            values.update({'property_account_position': template_user.property_account_position})
        if template_user.property_product_pricelist:
            values.update({'property_product_pricelist': template_user.property_product_pricelist})
        return super(auth_signup_sale, self)._signup_create_user(cr, uid, values, context)