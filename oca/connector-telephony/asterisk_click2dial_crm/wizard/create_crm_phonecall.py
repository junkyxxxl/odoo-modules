# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    @author: Jesús Martín <jmartin@zikzakmedia.com>
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _


class wizard_create_crm_phonecall(orm.TransientModel):
    _name = "wizard.create.crm.phonecall"

    def button_create_outgoing_phonecall(self, cr, uid, ids, context=None):
        partner = self.pool['res.partner'].browse(cr, uid, context.get('partner_id'), context=context)
        return self._create_open_crm_phonecall(cr, uid, partner, crm_categ='Outbound', context=context)

    def _create_open_crm_phonecall(self, cr, uid, partner, crm_categ, context=None):
        if context is None:
            context = {}
        categ_ids = self.pool['crm.case.categ'].search(cr, uid, [('name','=',crm_categ)], context={'lang': 'en_US'})
        case_section_ids = self.pool['crm.case.section'].search(cr, uid, [('member_ids', 'in', uid)], context=context)
        context.update({
            'default_partner_id': partner.id or False,
            'default_partner_phone': partner.phone,
            'default_partner_mobile': partner.mobile,
            'default_categ_id': categ_ids and categ_ids[0] or False,
            'default_section_id': case_section_ids and case_section_ids[0] or False,
        })

        return {
            'name': partner.name,
            'domain': [('partner_id', '=', partner.id)],
            'res_model': 'crm.phonecall',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'type': 'ir.actions.act_window',
            'nodestroy': False, # close the pop-up wizard after action
            'target': 'current',
            'context': context,
        }


class wizard_open_crm_leads(orm.TransientModel):
    _name = "wizard.open.crm.leads"

    def _create_open_crm_lead_no_partner(self, cr, uid, calling_number, crm_categ, context=None):
        '''Thanks to the crm_egt_leads method, we are able to query Asterisk and
        get the corresponding leads when we launch the wizard'''
        res = {}
        #calling_number = self.pool['asterisk.server']._get_calling_number(cr, uid, context=context)
        #To test the code without Asterisk server
        calling_number = "287644"
        if calling_number:
            res['calling_number'] = calling_number
            lead = self.pool['crm.lead'].get_lead_from_phone_number(cr, uid, calling_number, context=context)
            if lead:
                #res['partner_id'] = partner[0]
                #res['parent_partner_id'] = partner[1]
                res['lead_ids'] = lead
            else:
                res['partner_id'] = False
                res['parent_partner_id'] = False
            res['to_update_partner_id'] = False
        else:
            _logger.debug("Could not get the calling number from Asterisk.")
            raise osv.except_osv(_('Error :'), _("Could not get the calling number from Asterisk. Is your phone ringing or are you currently on the phone ? If yes, check your setup and look at the OpenERP debug logs."))

        if context is None:
            context = {}
        categ_ids = self.pool['crm.case.categ'].search(cr, uid, [('name','=',crm_categ)], context={'lang': 'en_US'})
        #TODO : switcher la vue si Lead ou Opportunity
        case_section_ids = self.pool['crm.case.section'].search(cr, uid, [('member_ids', 'in', uid)], context=context)

        return {
            'name': calling_number,
            'domain': [('id', 'in', lead),('type', 'in', categ_ids)],
            'res_model': 'crm.lead',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window.view',
            'nodestroy': False, # close the pop-up wizard after action
            'target': 'current',
            'context': context,
        }


class wizard_open_calling_partner(orm.TransientModel):
    _inherit = "wizard.open.calling.partner"

    def create_incoming_phonecall(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        partner = self.browse(cr, uid, ids[0], context=context).partner_id
        action = self.pool['wizard.create.crm.phonecall']._create_open_crm_phonecall(cr, uid, partner, crm_categ='Inbound', context=context)
        return action
    def open_leads_partner(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        '''Function called by the related button of the wizard'''
        #TODO : fixer le domaine à domain = [('type','=','lead')]
        return self.open_filtered_object(cr, uid, ids, self.pool.get('crm.lead'), context=context)
    def open_opportunity_partner(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        '''Function called by the related button of the wizard'''
        #TODO : fixer le domaine à domain = [('type','=','opportunity')]
        return self.open_filtered_object(cr, uid, ids, self.pool.get('crm.lead'), context=context)

    def open_leads_no_partner(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        callingnumber = self.browse (cr, uid, ids[0], context=context).partner_id
        action = self.pool['wizard.open.crm.leads']._create_open_crm_lead_no_partner(cr, uid, callingnumber, crm_categ='Lead', context=context)
        return action
    def open_opportunity_no_partner(self, cr, uid, ids, crm_categ, context=None):
        '''Started by button on 'open calling partner wizard'''
        callingnumber = self.browse (cr, uid, ids[0], context=context).partner_id
        action = self.pool['wizard.open.crm.leads']._create_open_crm_lead_no_partner(cr, uid, callingnumber, crm_categ='Opportunity', context=context)
        return action

