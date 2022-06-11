from odoo import models, fields,api


class ResCompany(models.Model):
    _inherit = 'res.company'

    ext_accounttant_invoice_email = fields.Char('Accounttant invoice email')
    ext_accounttant_bill_email = fields.Char('Accounttant bill email')

    
    
    
    