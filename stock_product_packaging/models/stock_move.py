from odoo import models, fields, api


class StockMoveProductPackaging(models.Model):
    _inherit = 'stock.move'

    product_package_qty_demand = fields.Float('Demand (Pack)', compute = '_compute_package_qty')
    product_package_qty_reserved = fields.Float('Reserved (Pack)', compute = '_compute_package_qty')
    product_package_qty_done = fields.Float('Done (pack)', compute = '_compute_package_qty')

    def _compute_package_qty(self):
        for line in self:
            if line.product_packaging_id and line.product_packaging_id.qty > 0:
                line.product_package_qty_demand = line.product_uom_qty / line.product_packaging_id.qty 
                line.product_package_qty_reserved = line.reserved_availability / line.product_packaging_id.qty
                line.product_package_qty_done = line.quantity_done / line.product_packaging_id.qty 
            else:
                line.product_package_qty_demand = 0
                line.product_package_qty_reserved = 0
                line.product_package_qty_done = 0



        

           

