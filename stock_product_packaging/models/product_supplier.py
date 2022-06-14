from odoo import models, fields, api


class ProductSupplierPackaging(models.Model):
    _inherit = 'product.supplierinfo'

    product_package_qty = fields.Float('Package qty', compute='_compute_package_qty')
    product_packaging_id = fields.Many2one('product.packaging')

    @api.onchange('min_qty','product_packaging_id')
    def _compute_package_qty(self):
        for line in self:
            if line.product_packaging_id and line.product_packaging_id.qty > 0:
                line.product_package_qty = line.min_qty / line.product_packaging_id.qty 
            else:
                line.product_package_qty = 0