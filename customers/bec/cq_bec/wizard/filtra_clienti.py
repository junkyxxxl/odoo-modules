# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Noviat nv/sa (www.noviat.be). All rights reserved.
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

from openerp.osv import osv, fields
import logging
_logger = logging.getLogger(__name__)


class res_partner_filtraclienti(osv.osv_memory):
    _name = 'res.partner.filtraclienti'
    _description = 'Filtra clienti per categorie / settori / attivita BEC'
    _columns = {
        'categoria': fields.many2one('res.partner.categoria', 'Categoria', ondelete='cascade'),
        'figli_cat': fields.boolean('Anche sotto-categorie'),
        'settore': fields.many2one('res.partner.settore', 'Settore', ondelete='cascade'),
        'figli_set': fields.boolean('Anche sotto-settori'),
        'attivita': fields.many2one('res.partner.attivita', 'Attivita', ondelete='cascade'),
        'figli_att': fields.boolean('Anche sotto-attivita'),
        'contatti': fields.boolean('Anche contatti'),
    }

    _defaults = {'contatti': True, }

    def add_cat(self, cr, uid, ids, context=None):
        # cerca eventuali categorie figlie e le aggiunge alla lista
        categ_obj = self.pool.get('res.partner.categoria')
        categ_ids = categ_obj.search(cr, uid, [('parent_id', 'in', ids)])
        if not categ_ids:
            return ids
        child_cat = self.add_cat(cr, uid, categ_ids)
        for child_id in child_cat:
            if child_id not in ids:
                ids.append(child_id)
        return ids

    def add_set(self, cr, uid, ids, context=None):
        # cerca eventuali settori figli e li aggiunge alla lista
        settor_obj = self.pool.get('res.partner.settore')
        settor_ids = settor_obj.search(cr, uid, [('parent_id', 'in', ids)])
        if not settor_ids:
            return ids
        child_set = self.add_set(cr, uid, settor_ids)
        for child_id in child_set:
            if child_id not in ids:
                ids.append(child_id)
        return ids

    def add_att(self, cr, uid, ids, context=None):
        # cerca eventuali attivita figlie e le aggiunge alla lista
        attiv_obj = self.pool.get('res.partner.attivita')
        attiv_ids = attiv_obj.search(cr, uid, [('parent_id', 'in', ids)])
        if not attiv_ids:
            return ids
        child_att = self.add_att(cr, uid, attiv_ids)
        for child_id in child_att:
            if child_id not in ids:
                ids.append(child_id)
        return ids

    def get_domain_clienti(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        data = self.browse(cr, uid, ids, context=context)
        categoria = data.categoria and data.categoria.id or None
        figli_cat = data.figli_cat
        settore = data.settore and data.settore.id or None
        figli_set = data.figli_set
        attivita = data.attivita and data.attivita.id or None
        figli_att = data.figli_att
        contatti = data.contatti

        cat_search = False
        if categoria:
            # aggiungo gli eventuali figli della categoria richiesta, se richiesti
            if figli_cat:
                cat_search = self.add_cat(cr, uid, [categoria])
            else:
                cat_search = [categoria]

        set_search = False
        if settore:
            # aggiungo gli eventuali figli del settore richiesto, se richiesti
            if figli_set:
                set_search = self.add_set(cr, uid, [settore])
            else:
                set_search = [settore]

        att_search = False
        if attivita:
            # aggiungo gli eventuali figli dell'attivita richiesta, se richiesti
            if figli_att:
                att_search = self.add_att(cr, uid, [attivita])
            else:
                att_search = [attivita]

        domain = []
        if cat_search:
            if set_search or att_search:
                domain.append('&')
            if contatti:
                domain.append('|')
                domain.append(('categoria_ids.name', 'in', cat_search))
                domain.append(('parent_id.categoria_ids.name', 'in', cat_search))
            else:
                domain.append(('categoria_ids.name', 'in', cat_search))
        if set_search:
            if att_search:
                domain.append('&')
            if contatti:
                domain.append('|')
                domain.append(('settore_ids.name', 'in', set_search))
                domain.append(('parent_id.settore_ids.name', 'in', set_search))
            else:
                domain.append(('settore_ids.name', 'in', set_search))
        if att_search:
            if contatti:
                domain.append('|')
                domain.append(('attivita_ids.name', 'in', att_search))
                domain.append(('parent_id.attivita_ids.name', 'in', att_search))
            else:
                domain.append(('attivita_ids.name', 'in', att_search))
        return domain

    def filtra_clienti(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        domain = self.get_domain_clienti(cr, uid, ids, context)

        return {'name': 'Ricerca Clienti',
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': domain,
                }
