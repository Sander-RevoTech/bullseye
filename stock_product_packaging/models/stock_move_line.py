from odoo import models, fields, api


class StockMoveLineProductPackaging(models.Model):
    _inherit = 'stock.move.line'

    product_package_qty_reserved = fields.Float('Package qty', compute = '_compute_package_qty')
    product_package_qty_done = fields.Float('Package qty', compute = '_compute_package_qty')
    product_packaging_id = fields.Many2one(related="move_id.product_packaging_id")

    def _compute_package_qty(self):
        for line in self:
            if line.move_id.product_packaging_id and line.move_id.product_packaging_id.qty > 0:
                line.product_package_qty_reserved = line.product_uom_qty / line.move_id.product_packaging_id.qty 
                line.product_package_qty_done = line.qty_done / line.move_id.product_packaging_id.qty 
            else:
                line.product_package_qty_reserved = 0
                line.product_package_qty_done = 0



        

           

