# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 ISA srl (<http://www.isa.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class hr_accredia_changes_entity(orm.TransientModel):
    _name = 'hr.accredia.changes.entity'
    _description = 'Changes Sensible Information'

    def _default_subaccount_auto_generation_customer(self, cr, uid, context=None):
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        t_value = my_company.subaccount_auto_generation_customer
        return t_value

    def _default_subaccount_auto_generation_supplier(self, cr, uid, context=None):
        res_users_obj = self.pool.get('res.users')
        my_company = res_users_obj.browse(cr, uid, uid).company_id
        t_value = my_company.subaccount_auto_generation_supplier
        return t_value

    def _default_check_customer(self, cr, uid, context=None):
        partner_obj = self.pool.get('res.partner') 
        t_entity_id = context.get('default_entity_id')
        t_entity = partner_obj.browse(cr, uid, t_entity_id)
        t_value = t_entity.customer
        return t_value

    def _default_check_supplier(self, cr, uid, context=None):
        partner_obj = self.pool.get('res.partner') 
        t_entity_id = context.get('default_entity_id')
        t_entity = partner_obj.browse(cr, uid, t_entity_id)
        t_value = t_entity.supplier
        return t_value

    def _default_check_individual(self, cr, uid, context=None):
        partner_obj = self.pool.get('res.partner') 
        t_entity_id = context.get('default_entity_id')
        t_entity = partner_obj.browse(cr, uid, t_entity_id)
        t_value = t_entity.individual
        return t_value

    _columns = {
        'entity_id': fields.many2one('res.partner',
                                     'Entity Id'),
        'legal_name': fields.char('Legal Name',
                                  size=128),
        'vat_code': fields.char('Vat Code',
                                size=64),
        'fiscal_code': fields.char('Fiscal Code',
                                   size=32,),
        'accounting_receivable_code': fields.char('Accounting Receivable Code',
                                                  size=128),
        'accounting_payable_code': fields.char('Accounting Payable Code',
                                               size=128),
        'accounting_receivable_code_id': fields.many2one('account.account',
                                                         'Accounting Receivable Code'),
        'accounting_payable_code_id': fields.many2one('account.account',
                                                      'Accounting Payable Code'),
        'reason': fields.text("Reason"),

        'customer': fields.related('entity_id',
                                   'customer',
                                   type='boolean',
                                   string='Customer', readonly=1),
        'supplier': fields.related('entity_id',
                                   'supplier',
                                   type='boolean',
                                   string='Supplier', readonly=1),
        'is_entity': fields.related('entity_id',
                                    'is_entity',
                                    type='boolean',
                                    string='Is Entity', readonly=1),
        'individual': fields.related('entity_id',
                                     'individual',
                                     type='boolean',
                                     string='Persona Fisica', readonly=1),
        'subaccount_auto_generation_customer': fields.related('entity_id',
                                                              'company_id',
                                                              'subaccount_auto_generation_customer',
                                                              type='boolean',
                                                              string='Customers Subaccount Automatic Generation', readonly=1),
        'subaccount_auto_generation_supplier': fields.related('entity_id',
                                                              'company_id',
                                                              'subaccount_auto_generation_supplier',
                                                              type='boolean',
                                                              string='Suppliers Subaccount Automatic Generation', readonly=1),
        'street': fields.char('Indirizzo', size=128),
        'city': fields.char('Città', size=128),
        'zip': fields.char('CAP', change_default=True, size=24),
        'province': fields.many2one('res.province',
                                    string='Provincia'),
        'region': fields.many2one('res.region',
                                  string='Regione'),
        'country_id': fields.many2one('res.country',
                                      'Nazione'),
        'validity_date': fields.date('Data Validità'),
    }

    _defaults = {'customer': _default_check_customer,
                 'supplier': _default_check_supplier,
                 'individual': _default_check_individual,
                 'subaccount_auto_generation_customer': _default_subaccount_auto_generation_customer,
                 'subaccount_auto_generation_supplier': _default_subaccount_auto_generation_supplier,
                 }

    def confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = context.copy()

        entity_obj = self.pool.get('res.partner')
        changelog_obj = self.pool.get('accreditation.changelog')
        user_obj = self.pool.get('res.users')

        my_company = user_obj.browse(cr, uid, uid).company_id
        t_wizard_data = self.browse(cr, uid, ids[0])
        old_partner_id = t_wizard_data.entity_id.id
        old_partner_data = entity_obj.browse(cr, uid, old_partner_id)

        if old_partner_data.vat == t_wizard_data.vat_code:
            ctx.update({
                'avoid_subaccount_generation': True,
                'old_partner_id': old_partner_id,
            })

        dict_entity = {'name': t_wizard_data.legal_name,
                       'vat': t_wizard_data.vat_code,
                       'fiscalcode': t_wizard_data.fiscal_code,
                       'street': t_wizard_data.street,
                       'city': t_wizard_data.city,
                       'zip': t_wizard_data.zip,
                       'province': t_wizard_data.province.id,
                       'region': t_wizard_data.region.id,
                       'country_id': t_wizard_data.country_id.id,
                       }

        new_partner_id = entity_obj.copy(cr,
                                         uid,
                                         old_partner_id,
                                         dict_entity,
                                         context=ctx)

        entity_obj.write(cr, uid, [old_partner_id], {'entity_changed': True})

        dict_changelog = {'authorized_user_id': uid,
                          'partner_id_old': old_partner_id,
                          'partner_id_new': new_partner_id,
                          'comments': t_wizard_data.reason,
                          'validity_date': t_wizard_data.validity_date,
                          }
        changelog_obj.create(cr, uid, dict_changelog)

        if old_partner_data.vat != t_wizard_data.vat_code:
            if not my_company.subaccount_auto_generation_customer:
                entity_obj.write(cr, uid,
                                 [new_partner_id],
                                 {'property_account_receivable': t_wizard_data.accounting_receivable_code_id.id})

                if not my_company.subaccount_auto_generation_supplier:
                    if old_partner_data.supplier:
                        entity_obj.write(cr, uid,
                                         [new_partner_id],
                                         {'property_account_payable': t_wizard_data.accounting_payable_code_id.id})
                    else:
                        entity_obj.write(cr, uid,
                                         [new_partner_id],
                                         {'property_account_payable': t_wizard_data.accounting_receivable_code_id.id})

        self.do_change_project_partner(cr, uid, ids, old_partner_id, new_partner_id)

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'hr_accredia',
                                              'view_res_partner_accreditation_entity_form')
        view_id = result and result[1] or False
        return {'name': _('New Entity'),
                'res_model': 'res.partner',
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': int(new_partner_id),
                'context': ctx,
                'target': 'inlineview',
                }

    def do_change_project_partner(self, cr, uid, ids, old_id, new_id, context=None):
        proj_obj = self.pool.get('project.project')
        project_ids = proj_obj.search(cr, uid, [('partner_id', '=', old_id)])
        res = proj_obj.write(cr, uid, project_ids, {'partner_id': new_id})
        if not res:
            raise orm.except_orm(_('Error!'),
                                 _('Errore durante sostituzione nuovo ente nei processi!'))
        return res

    def button_check_vat(self, cr, uid, ids, context=None):
        t_partner = self.browse(cr, uid, ids[0])
        t_vat_code = t_partner.vat_code
        entity_obj = self.pool.get('res.partner')
        vat_country, vat_number = entity_obj._split_vat(t_vat_code)
        result = entity_obj.simple_vat_check(cr, uid, vat_country, vat_number, context=context)
        if not result:
            raise orm.except_orm(_('Error!'), _('Codice Partita Iva Non Valido!'))
        # TODO migliorare?
        raise orm.except_orm(_('OK!'), _('Codice Partita Iva Valido!'))
        return None
