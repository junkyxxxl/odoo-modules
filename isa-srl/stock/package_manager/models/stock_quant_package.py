# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 ISA s.r.l. (<http://www.isa.it>).
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

from openerp.osv import fields, osv

class stock_quant_package(osv.osv):
    
    _inherit = 'stock.quant.package' 
    
    
    def _get_package_info(self, cr, uid, ids, name, args, context=None):
        #Richiamo la funzione base situata in "stock"
        return super(stock_quant_package, self)._get_package_info(cr, uid, ids, name, args, None)


    def _get_packages(self, cr, uid, ids, context=None):
        #Richiamo la funzione base situata in "stock"
        return super(stock_quant_package, self)._get_packages(cr, uid, ids, None)
    
    
    def _get_packages_to_relocate(self, cr, uid, ids, context=None):
        #Richiamo la funzione base situata in "stock"
        return super(stock_quant_package, self)._get_packages_to_relocate(cr, uid, ids, None)    


    #Definisco la funzione che dovrà essere richiamata nel caso in cui cambi il "package_id" in "stock.quant"
    def _get_packages_to_recompute(self, cr, uid, ids, context=None):
      #In questa maniera in control_context: se non esiste il campo 'recompute', di Default lo assegna False, altrimenti reperisce il valore 
      control_context = context.get('recompute', False)
      res = set()
      if control_context:
        for quant in self.browse(cr, uid, ids, context=context):
            pack = quant.package_id
            while pack:
                res.add(pack.id)
                pack = pack.parent_id
      return list(res)
      
 
        
    #Con store vuol dire che se cambia la 'location_id' in 'stock.quant', viene richiamata la funzione '_get_packages' 
    #oppure se vengono modificate le righe quant in 'stock.quant.package'.
    #Viene aggiunta un'altra condizione in cui se cambia il pacco in 'stock.quant' allora viene richiamata la funzione che è stata creata
    _columns = {
        'location_id': fields.function(_get_package_info, type='many2one', relation='stock.location', string='Location', multi="package",
                                    store={
                                       'stock.quant': (_get_packages, ['location_id'], 10),
                                       'stock.quant.package': (_get_packages_to_relocate, ['quant_ids', 'children_ids', 'parent_id'], 10),
                                       'stock.quant': (_get_packages_to_recompute, ['package_id'],10),
                                    }, readonly=True, select=True),
        'company_id': fields.function(_get_package_info, type="many2one", relation='res.company', string='Company', multi="package", 
                                    store={
                                       'stock.quant': (_get_packages, ['company_id'], 10),
                                       'stock.quant.package': (_get_packages_to_relocate, ['quant_ids', 'children_ids', 'parent_id'], 10),
                                       'stock.quant': (_get_packages_to_recompute, ['package_id'],10),
                                    }, readonly=True, select=True),
    }
    
        
        
    



    

     
    

           
      
    
    
    
    
    