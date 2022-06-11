from odoo import models,fields,api
from odoo.tools import float_is_zero, float_compare, float_round

class StockReturnPickingLine(models.TransientModel):
    _inherit = 'stock.return.picking.line'

    product_packaging_id = fields.Many2one('product.packaging', readonly=True)
    product_packaging_qty = fields.Float('Produdct Packaging Qty')

    @api.onchange('product_packaging_qty')
    def on_change_product_packaging_qty(self):
        if self.product_packaging_id:
            packaging_uom = self.product_packaging_id.product_uom_id
            qty_per_packaging = self.product_packaging_id.qty
            product_uom_qty = packaging_uom._compute_quantity(self.product_packaging_qty * qty_per_packaging, self.uom_id)
            if float_compare(product_uom_qty, self.quantity, precision_rounding=self.uom_id.rounding) != 0:
                self.quantity = product_uom_qty
        else:
            self.product_packaging_qty = False

    @api.onchange('quantity')
    def on_change_product_qty(self):
        if not self.product_packaging_id:
            self.product_packaging_qty = False
        else:
            packaging_uom = self.product_packaging_id.product_uom_id
            packaging_uom_qty = self.uom_id._compute_quantity(self.quantity, packaging_uom)
            self.product_packaging_qty = float_round(packaging_uom_qty / self.product_packaging_id.qty, precision_rounding=packaging_uom.rounding)

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    
    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        result = super(StockReturnPicking,self)._prepare_stock_return_picking_line_vals_from_move(stock_move)
        packaging = stock_move.product_packaging_id
        pack_qty = False
        if packaging:
            pack_qty = result['quantity'] / packaging.qty

        result.update({
            'product_packaging_id': packaging.id,
            'product_packaging_qty': pack_qty
        })
        return result
