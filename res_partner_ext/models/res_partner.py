from ctypes.wintypes import tagSIZE
from unicodedata import category

from attr import fields
from odoo import models, fields


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'
    _description = 'Res Partner Category'
    

    supplier_tag = fields.Boolean('Supplier Tag')
    customer_tag = fields.Boolean('Customer Tag')
    

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    supplier_tags = fields.Many2many('res.partner.category', column1='partner_id', relation='res_partner_category_supplier_rel',
                                    column2='category_id', string='Supplier Tags', domain=[('supplier_tag', '=', True)])

    customer_tags = fields.Many2many('res.partner.category', column1='partner_id', relation='res_partner_category_customer_rel',
                                    column2='category_id', string='Customer Tags', domain=[('customer_tag', '=', True)])
    