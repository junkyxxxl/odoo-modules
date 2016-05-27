# -*- coding: utf-8 -*-
from openerp import models, api


class stock_pack_operation(models.Model):

    _inherit = ['stock.pack.operation']

    @api.model
    def operation_exists(self, picking_id, barcode_str, visible_op_ids):
        if self._context is None:
            self._context = {}
        domain = self._process_barcode_for_exists(barcode_str)
        if not domain:
            # Se non ho trovato il dominio (non si dovrebbe mai verificare)
            # assumo il true per far proseguir la funzione secondo lo standard.
            return True
        package_clause = [('result_package_id', '=', self._context.get('current_package_id', False))]
        existing_operation_ids = self.search([('picking_id', '=', picking_id)] + domain + package_clause)
        existing_operation_id = existing_operation_ids[0] if len(existing_operation_ids) > 1 else existing_operation_ids
        if existing_operation_id:
            return {
                'find': True,
                'product_id': existing_operation_id.product_id.id
            }
        else:
            return {
                'find': False,
                'product_id': False
            }

    @api.model
    def get_barcode_configuration(self):
        company = self.env.user.company_id
        decimal_precision = False
        decimal_precision = self.env['decimal.precision'].search([('name', '=', 'Product Unit of Measure')])
        if decimal_precision:
            number_decimal = decimal_precision.digits
        return {
            'play_sound_larger_amount': company.larger_amount,
            'play_sound_article_not_available': company.article_not_available,
            'confirmation_article_not_available': company.confirmation_article_not_available,
            'picking_list_type_id': company.picking_list_type_id.id,
            'check_quantity': company.check_quantity,
            'force_check_quantity': company.force_check_quantity,
            'number_decimal': number_decimal
        }

    def _process_barcode_for_exists(self, barcode_str):
        product_obj = self.env['product.product']
        lot_obj = self.env['stock.production.lot']
        package_obj = self.env['stock.quant.package']
        matching_product_ids = product_obj.search(['|', ('ean13', '=', barcode_str), ('default_code', '=', barcode_str)])
        # Cerco per prodotto
        if matching_product_ids:
            return [('product_id', '=', matching_product_ids[0].id)]
        # Cerco per lotto
        matching_lot_ids = lot_obj.search([('name', '=', barcode_str)])
        if matching_lot_ids:
            lot = lot_obj.browse(matching_lot_ids[0].id)
            return [('product_id', '=', lot.product_id.id), ('lot_id', '=', lot.id)]
        # Cerco per pacco
        matching_package_ids = package_obj.search([('name', '=', barcode_str)])
        if matching_package_ids:
            return [('package_id', '=', matching_package_ids[0].id)]
        return None

    @api.model
    def search_lot(self, package_id):
        res = {'lots': []}
        if not package_id:
            return res
        product = self.browse(package_id).product_id
        if product:
            stock_productions = self.env['stock.production.lot'].search([('product_id', '=', product.id)])
            lots = [stock_production.name for stock_production in stock_productions]
            res.update({'lots': lots})
        return res
