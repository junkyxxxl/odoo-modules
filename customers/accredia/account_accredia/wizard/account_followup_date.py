# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import datetime
import time

from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_followup_date(osv.osv_memory):
    _name = 'account_followup.date'
    _description = 'Print Follow-up & Send Mail to Customers'
    _columns = {'department_id': fields.many2one('hr.department',
                                                 'Dipartimento'),
                'date': fields.date('Data Calcolo Scaduto', required=True,
                                    help="This field allow you to select a forecast date to plan your follow-ups"),
                'followup_id': fields.many2one('account_followup.followup', 'Follow-Up', required=True, readonly = True),
                'partner_ids': fields.many2many('account_followup.stat.by.partner', 'partner_stat_rel', 
                                                'osv_memory_id', 'partner_id', 'Partners', required=True),
                'company_id': fields.related('followup_id', 'company_id', type='many2one',
                                             relation='res.company', store=True, readonly=True),
                'partner_id': fields.many2one('res.partner', 'Partner'),
                'email_conf': fields.boolean('Send Email Confirmation'),
                'email_subject': fields.char('Email Subject', size=64),
                'partner_lang': fields.boolean('Send Email in Partner Language',
                                               help='Do not change message text, if you want to send email in partner language, or configure from company'),
                'email_body': fields.text('Email Body'),
                'summary': fields.text('Summary', readonly=True),
                'test_print': fields.boolean('Test Print',
                                             help='Check if you want to print follow-ups without changing follow-up level.'),
                }

    def _get_followup(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('active_model', 'ir.ui.menu') == 'account_followup.followup':
            return context.get('active_id', False)
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        followp_id = self.pool.get('account_followup.followup').search(cr, uid, [('company_id', '=', company_id)], context=context)
        return followp_id and followp_id[0] or False

    def process_partners(self, cr, uid, partner_ids, data, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_ids_to_print = []
        nbmanuals = 0
        manuals = {}
        nbmails = 0
        nbunknownmails = 0
        nbprints = 0
        resulttext = " "
        for partner in self.pool.get('account_followup.stat.by.partner').browse(cr, uid, partner_ids, context=context):
            if partner.max_followup_id.manual_action:
                partner_obj.do_partner_manual_action(cr, uid, [partner.partner_id.id], context=context)
                nbmanuals = nbmanuals + 1
                key = partner.partner_id.payment_responsible_id.name or _("Anybody")
                if not key in manuals.keys():
                    manuals[key]= 1
                else:
                    manuals[key] = manuals[key] + 1
            if partner.max_followup_id.send_email:
                nbunknownmails += partner_obj.do_partner_mail(cr, uid, [partner.partner_id.id], context=context)
                nbmails += 1
            if partner.max_followup_id.send_letter:
                partner_ids_to_print.append(partner.id)
                nbprints += 1
                message = "%s<I> %s </I>%s" % (_("Follow-up letter of "), partner.partner_id.latest_followup_level_id_without_lit.name, _(" will be sent"))
                partner_obj.message_post(cr, uid, [partner.partner_id.id], body=message, context=context)
        if nbunknownmails == 0:
            resulttext += str(nbmails) + _(" email(s) sent")
        else:
            resulttext += str(nbmails) + _(" email(s) should have been sent, but ") + str(nbunknownmails) + _(" had unknown email address(es)") + "\n <BR/> "
        resulttext += "<BR/>" + str(nbprints) + _(" letter(s) in report") + " \n <BR/>" + str(nbmanuals) + _(" manual action(s) assigned:")
        needprinting = False
        if nbprints > 0:
            needprinting = True
        resulttext += "<p align=\"center\">"
        for item in manuals:
            resulttext = resulttext + "<li>" + item + ":" + str(manuals[item]) +  "\n </li>"
        resulttext += "</p>"
        result = {}
        action = partner_obj.do_partner_print(cr, uid, partner_ids_to_print, data, context=context)
        result['needprinting'] = needprinting
        result['resulttext'] = resulttext
        result['action'] = action or {}
        return result

    def do_update_followup_level(self, cr, uid, to_update, partner_list, date, context=None):
        # update the follow-up level on account.move.line
        for id in to_update.keys():
            if to_update[id]['partner_id'] in partner_list:
                self.pool.get('account.move.line').write(cr, uid, [int(id)], {'followup_line_id': to_update[id]['level'], 
                                                                              'followup_date': date})

    def clear_manual_actions(self, cr, uid, partner_list, context=None):
        # Partnerlist is list to exclude
        # Will clear the actions of partners that have no due payments anymore
        partner_list_ids = [partner.partner_id.id for partner in self.pool.get('account_followup.stat.by.partner').browse(cr, uid, partner_list, context=context)]
        ids = self.pool.get('res.partner').search(cr, uid, ['&', ('id', 'not in', partner_list_ids), '|', 
                                                             ('payment_responsible_id', '!=', False), 
                                                             ('payment_next_action_date', '!=', False)], context=context)

        partners_to_clear = []
        for part in self.pool.get('res.partner').browse(cr, uid, ids, context=context): 
            if not part.unreconciled_aml_ids: 
                partners_to_clear.append(part.id)
        self.pool.get('res.partner').action_done(cr, uid, partners_to_clear, context=context)
        return len(partners_to_clear)

    def do_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.browse(cr, uid, ids, context=context)[0]
        t_date = data.date
        t_department = data.department_id and data.department_id.id or None

        context.update({'Followupfirst': True,
                        'search_default_todo': True,
                        'default_dom_department_id': t_department,
                        'default_dom_date': t_date,
                        })
        if t_date:
            context.update({'date_ref': t_date})
        if t_department:
            context.update({'department_id': t_department})

        mod_obj = self.pool.get('ir.model.data')
        result = mod_obj.get_object_reference(cr, uid,
                                              'account_followup',
                                              'customer_followup_tree')
        view_id = result and result[1] or False

        result = mod_obj.get_object_reference(cr, uid,
                                              'account_followup',
                                              'customer_followup_search_view')
        search_view_id = result and result[1] or False

        if data.partner_id:
            result = mod_obj.get_object_reference(cr, uid,
                                                  'account_accredia',
                                                  'view_partner_inherit_followup_form_accredia')

            view_id = result and result[1] or False

            context.update({'Followupfirst': True,
                            'search_default_todo': True,
                            'search_default_my': True,
                            })

            return {
                'name': _('Solleciti Manuali'),
                'view_type': 'form',
                'res_id': data.partner_id.id,
                'context': context,
                'view_id': view_id,
                'view_mode': 'form',
                'res_model': 'res.partner',
                'domain': "[('payment_amount_due', '>', 0.0)]",
                'search_view_id': search_view_id,
                'type': 'ir.actions.act_window',
                'target': 'current',
                }

        return {
            'name': _('Solleciti Manuali'),
            'view_type': 'form',
            'context': context,
#            'view_id': view_id,
            'views': [(view_id,'tree'),(False,'form')],
            'view_mode': 'tree,form',
            'res_model': 'res.partner',
            'domain': "[('payment_amount_due', '>', 0.0)]",
            'search_view_id': search_view_id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            }

    def _get_msg(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.follow_up_msg

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'followup_id': _get_followup,
        'email_body': "",
        'email_subject': _('Invoices Reminder'),
        'partner_lang': True,
    }

    def _get_partners_followp(self, cr, uid, ids, context=None):

        data = self.browse(cr, uid, ids, context=context)[0]
        company_id = data.company_id.id

        cr.execute(
            "SELECT l.partner_id, l.followup_line_id,l.date_maturity, l.date, l.id "\
            "FROM account_move_line AS l "\
                "LEFT JOIN account_account AS a "\
                "ON (l.account_id=a.id) "\
            "WHERE (l.reconcile_id IS NULL) "\
                "AND (a.type='receivable') "\
                "AND (l.state<>'draft') "\
                "AND (l.partner_id is NOT NULL) "\
                "AND (a.active) "\
                "AND (l.debit > 0) "\
                "AND (l.company_id = %s) " \
                "AND (l.blocked = False)" \
            "ORDER BY l.date", (company_id,))  #l.blocked added to take litigation into account and it is not necessary to change follow-up level of account move lines without debit
        move_lines = cr.fetchall()
        old = None
        fups = {}
        fup_id = 'followup_id' in context and context['followup_id'] or data.followup_id.id

        # TODO?
        date = 'date' in context and context['date'] or data.date

        current_date = datetime.date(*time.strptime(date,
            '%Y-%m-%d')[:3])
        cr.execute(
            "SELECT * "\
            "FROM account_followup_followup_line "\
            "WHERE followup_id=%s "\
            "ORDER BY delay", (fup_id,))

        #Create dictionary of tuples where first element is the date to compare with the due date and second element is the id of the next level
        for result in cr.dictfetchall():
            delay = datetime.timedelta(days=result['delay'])
            fups[old] = (current_date - delay, result['id'])
            old = result['id']

        partner_list = []
        to_update = {}

        #Fill dictionary of accountmovelines to_update with the partners that need to be updated
        for partner_id, followup_line_id, date_maturity,date, id in move_lines:
            if not partner_id:
                continue
            if followup_line_id not in fups:
                continue
            stat_line_id = partner_id * 10000 + company_id
            if date_maturity:
                if date_maturity <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                    if stat_line_id not in partner_list:
                        partner_list.append(stat_line_id)
                    to_update[str(id)]= {'level': fups[followup_line_id][1], 'partner_id': stat_line_id}
            elif date and date <= fups[followup_line_id][0].strftime('%Y-%m-%d'):
                if stat_line_id not in partner_list:
                    partner_list.append(stat_line_id)
                to_update[str(id)]= {'level': fups[followup_line_id][1], 'partner_id': stat_line_id}
        return {'partner_ids': partner_list, 'to_update': to_update}
