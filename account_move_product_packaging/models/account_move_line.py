from ast import mod
from odoo import models, fields, api, exceptions

class account_move_product_packaging_qty(models.Model):
    _inherit='account.move'

    @api.model
    def create(self,values):
        invoices = super(account_move_product_packaging_qty,self).create(values)
        for invoice in invoices:
            for line in invoice.invoice_line_ids:
                line._onchange_product_id_update_product_packaging()
        return invoices

class account_move_line(models.Model):
    _inherit = 'account.move.line'

    product_packaging_id = fields.Many2one(comodel_name='product.packaging', string='Packaging', domain="[('product_id','=',product_id),('sales', '=', True)]")
    product_packaging_qty = fields.Float('Package Quantity')

    @api.onchange('product_id')
    def _onchange_product_id_update_product_packaging(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            product_packagings = self.env['product.packaging'].search([('product_id', '=', line.product_id.id)])
            if len(product_packagings) == 0:
                continue

            line.product_packaging_id = product_packagings[0].id
            line.product_packaging_qty = self.quantity / product_packagings[0].qty

    @api.onchange('product_id')
    def _on_change_product_id_domain(self):
        return {
            'domain': {'product_packaging_id': 
            [
                ('product_id','=',self.product_id.id),
                ('sales', '=', True)
            ]}
        }

    @api.depends('quantity')
    @api.onchange('quantity')
    def _onchange_quantity_update_product_packaging(self):
        if self.product_id:
            product_packagings = self.env['product.packaging'].search([('product_id', '=', self.product_id.id)])
            if len(product_packagings) > 0 and product_packagings[0].qty:
                package_qty = self.quantity / product_packagings[0].qty
                self.product_packaging_qty = package_qty
    	    
    @api.onchange('product_packaging_qty')
    def _onchange_product_packaging_qty(self):
        if self.product_id:
            product_packagings = self.env['product.packaging'].search([('product_id', '=', self.product_id.id)])

            if len(product_packagings) > 0 and product_packagings[0].qty:
                product_qty_new = self.product_packaging_qty *  product_packagings[0].qty
                if round(product_qty_new,0) != self.quantity:
                    self.quantity = int(product_qty_new)
            else:
                self.product_packaging_qty = 0.00
                raise exceptions.ValidationError(f"Information! : Product {self.name} has not defined packaging. Package qty will be reset to 0.00")