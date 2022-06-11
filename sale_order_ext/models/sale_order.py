from odoo import models,fields,api

class saleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_to_credit = fields.Float(
        compute='_compute_qty_to_credit', string='Quantity To Credit', store=True,
        digits='Product Unit of Measure')

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity', 'untaxed_amount_to_invoice','qty_delivered')
    def _compute_qty_to_credit(self):
        for line in self:
            qty_to_credit = line.qty_invoiced - line.qty_delivered
            if qty_to_credit < 0:
                qty_to_credit = 0
            line.qty_to_credit = qty_to_credit

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_create_credit = fields.Boolean(compute='_compute_show_create_credit')


    def _compute_show_create_credit(self):
        for order in self:
            order.show_create_credit = False
            lines = order.order_line.filtered(lambda line: line.qty_to_credit > 0)
            invoices = order.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
            if len(lines) and invoices:
                order.show_create_credit = True


    
    #Goal is to help the user and enter automatically the packaing
    @api.onchange('order_line')
    def on_change_product_id(self):
        for order in self:
            for line in order.order_line:
                if not line.product_packaging_id:
                    #Check if the product has some packaging assinged
                    if line.product_id.packaging_ids:
                        pack = line.product_id.packaging_ids[0]
                        if pack.sales and line.product_uom_qty == 1:
                            line.product_packaging_id = pack.id
                            line.product_uom_qty = pack.qty
                            line.product_packaging_qty = 1


    def action_create_credit(self):
        #We show a wizard where the user can select from which invoice he wants to reverse
        invoices = self.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted')
        if invoices:
            inv = invoices[0]

            invoice_val = self._prepare_invoice()
            invoice_val['move_type'] = 'out_refund'
            invoice_val['ref'] = 'Reversal of:' + inv.name

            sale_lines = self.order_line.filtered(lambda line: line.qty_to_credit > 0)
            invoice_line_vals = []
            invoice_item_sequence = 0
            for line in sale_lines:

                line_vals = line._prepare_invoice_line(sequence=invoice_item_sequence)
                line_vals['quantity'] = line.qty_to_credit

                invoice_line_vals.append(
                    (0, 0, line_vals))
                invoice_item_sequence += 1

            invoice_val['invoice_line_ids'] += invoice_line_vals
            
            credit = self.env['account.move'].sudo().with_context(default_move_type='out_refund').create(invoice_val)

            credit.message_post_with_view('mail.message_origin_link',
                values={'self': credit, 'origin': credit.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )

            action = {
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': credit.id,
            }
            return action


            




      