from odoo import models, fields, api

class StockPickingProductPackaging(models.Model):
    _inherit = 'stock.picking'

    date_done = fields.Datetime(tracking=True)
    total_product_package_qty = fields.Float('Total Package Quantity', compute = '_compute_total_package_qty',readonly = True)

    def _compute_total_package_qty(self):

        self.total_product_package_qty = 0
        for line in self.move_line_ids_without_package:
            
            if line.move_id.product_packaging_id and line.move_id.product_packaging_id.qty > 0:
                self.total_product_package_qty += line.product_package_qty_done