from email.mime import base
from odoo import models,api,fields
from odoo.exceptions import UserError

class StockPickingNotification(models.Model):
    _inherit = 'stock.picking'
   
    @api.model
    def create(self,values):
        res = super(StockPickingNotification,self).create(values)

        for picking in res:
            picking.send_email_notification()
        
        return res

    def action_confirm(self):
        res = super(StockPickingNotification,self).action_confirm()

        for picking in self:
            self.send_email_notification()

        return res


    def send_email_notification(self):
        self.ensure_one()
        picking_type = self.picking_type_id
        if not picking_type.notifi_employee_id:
            return
        
        if self.state == 'draft':
            return

        email_from = self.get_mail_from()
        mail_to = self.get_mail_to()
      
        #Create the mail body
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        body = '<p>A new transfer ' + self.name + ' has been created.</p>'
        body += '<a href="%s">View transfer: %s </p>'%(base_url,self.name)

        mail_vals = {
            'model': self._name,
            'res_id': self.id,
            'email_from': email_from,
            'email_to': mail_to,
            'subject': 'New Transfer: ' + self.name,
            'body_html': body}

        mail = self.env['mail.mail'].create(mail_vals)
        self.env['mail.mail'].send([mail])

    
    def get_mail_from(self):
        self.ensure_one()
        email_from = self.env.user.email
        if email_from == '' or email_from == False:
            raise UserError('You have no email configured on your account')
        
        return email_from

    def get_mail_to(self):
        self.ensure_one()
        mail_to = ''
        for employee in self.picking_type_id.notifi_employee_id:
            if not employee.work_email:
                raise UserError('No email set for %s'%(employee.name))
            else:
                mail_to = employee.work_email + ';'
        
        return mail_to