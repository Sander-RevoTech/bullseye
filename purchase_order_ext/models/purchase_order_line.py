from odoo import models,api

class PurchaseOrderLineExt(models.Model):
    _inherit = 'purchase.order.line'

    @api.model
    def _get_date_planned(self, seller, po=False):
        if not self.order_id.date_planned:
            return super(PurchaseOrderLineExt, self)._get_date_planned(seller,po)
        return self._convert_to_middle_of_day(self.order_id.date_planned)
    