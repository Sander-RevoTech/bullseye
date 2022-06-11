from odoo import models,fields,api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    #Goal is to help the user and enter automatically the packaing
    @api.onchange('order_line')
    def on_change_product_id(self):
        for order in self:
            for line in order.order_line:
                if not line.product_packaging_id:
                    #Check if the product has some packaging assinged
                    if line.product_id.packaging_ids:
                        pack = line.product_id.packaging_ids[0]
                        if pack.purchase and line.product_uom_qty == 1:
                            line.product_packaging_id = pack.id
                            line.product_qty = pack.qty
                            line.product_packaging_qty = 1