from odoo import models,fields,api

class StockPickingTypeNotifications(models.Model):
    _inherit = 'stock.picking.type'
    
    notifi_employee_id = fields.Many2many('hr.employee.public', 
        column1='product_tmpl_id',column2='employee_id',
        help='Employees that are listed here will receive a notification on receiving products')
    