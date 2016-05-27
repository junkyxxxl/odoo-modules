# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    Copyright (C) 2013 Invitu <contact@invitu.com>
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


class res_partner(orm.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'asterisk.common']

    def action_dial(self, cr, uid, ids, context=None):
        '''
        This method open the phone call history when the phone click2dial
        button of asterisk_click2dial module is pressed
        :return the phone call history view of the partner
        '''
        if context is None:
            context = {}
        super(res_partner, self).action_dial(cr, uid, ids, context=context)
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        context['partner_id'] = ids[0]
        action_start_wizard = {
            'name': 'Create phone call in CRM',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.create.crm.phonecall',
            'view_type': 'form',
            'view_mode': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': context,
            }
        if user.context_propose_creation_crm_call:
            return action_start_wizard
        else:
            return True



class res_users(orm.Model):
    _inherit = "res.users"

    _columns = {
        # Field name starts with 'context_' to allow modification by the user
        # in his preferences, cf server-61/openerp/addons/base/res/res_users.py
        # line 377 in "def write" of "class users"
        'context_propose_creation_crm_call': fields.boolean('Propose to create a call in CRM after a click2dial'),
        }

    _defaults = {
        'context_propose_creation_crm_call': True,
        }

class crm_lead(orm.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'asterisk.common']


    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).create(cr, uid, vals_reformated, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_lead, self).write(cr, uid, ids, vals_reformated, context=context)

    def get_lead_from_phone_number(self, cr, uid, presented_number, context=None):
        # We check that "number" is really a number
        _logger.debug(u"Call get_name_from_phone_number with number = %s" % presented_number)
        if not isinstance(presented_number, (str, unicode)):
            _logger.warning(u"Number '%s' should be a 'str' or 'unicode' but it is a '%s'" % (presented_number, type(presented_number)))
            return False
        if not presented_number.isdigit():
            _logger.warning(u"Number '%s' should only contain digits." % presented_number)
            return False

        ast_server = self.pool['asterisk.server']._get_asterisk_server_from_user(cr, uid, context=context)
        nr_digits_to_match_from_end = ast_server.number_of_digits_to_match_from_end
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[-nr_digits_to_match_from_end:len(presented_number)]
        else:
            end_number_to_match = presented_number

        _logger.debug("Will search phone and mobile numbers in crm.lead ending with '%s'" % end_number_to_match)

        # We try to match a phone or mobile number with the same end
        pg_seach_number = str('%' + end_number_to_match)
        res_ids = self.search(cr, uid, ['|', ('phone_e164', 'ilike', pg_seach_number), ('mobile_e164', 'ilike', pg_seach_number)], context=context)
        # TODO : use is_number_match() of the phonenumber lib ?
        if len(res_ids) > 1:
            _logger.warning(u"There are several leads (IDS = %s) with a phone number ending with '%s'" % (str(res_ids), end_number_to_match))
        if res_ids:
#            entry = self.read(cr, uid, res_ids[0], ['name', 'parent_id'], context=context)
#            _logger.debug(u"Answer get_lead_from_phone_number with name = %s" % entry['name'])
#            return (entry['id'], entry['parent_id'] and entry['parent_id'][0] or False, entry['name'])i
            return res_ids
        else:
            _logger.debug(u"No match for end of phone number '%s'" % end_number_to_match)
            return False

