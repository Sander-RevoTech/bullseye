from odoo import models,fields,api
from odoo.exceptions import UserError

import base64

class AccountMove(models.Model):
    _inherit = 'account.move'

    sent_to_accounttant = fields.Boolean('Sent To Accounttant', readonly=True)


    def send_to_accounttant(self):
        for move in self:
            if not self.state == 'posted':
                continue

            if move.move_type in ('out_invoice','out_refund'):
                move.send_invoice()

            elif move.move_type in ('in_invoice','in_refund'):
                move.send_bill()
            else:
                raise UserError('Type of %s is not supported',move.move_type)
            move.log_sent_to_accounttant()
                

    def send_invoice(self):
        self.ensure_one()
        email = self.env.company.ext_accounttant_invoice_email
        if not email:
            raise UserError('No email for invoicing configured')
        self.send_mail(email,'Invoice: ' + self.name)
      
        

    
    def send_bill(self):
        self.ensure_one()
        email = self.env.company.ext_accounttant_bill_email
        if not email:
            raise UserError('No email for billing configured')
        self.send_mail(email,'Bill: ' + self.name)

    def send_mail(self,mail_to,subject):
        email_from = self.env.user.email

        if email_from == '' or email_from == False:
            raise UserError('You have no email configured on your account')

        report = self.env['ir.actions.report']._get_report_from_name('account.report_invoice')
        pdf = report._render_qweb_pdf(self.id)
        # attachment =  self.env['ir.attachment'].create({
        #     'name': self.name.replace('/','_') + '.pdf',
        #     'type': 'binary',
        #     'datas': base64.b64encode(pdf[0]),
        #     'res_model': 'account.move',
        #     'res_id': self.id,
        #     'mimetype': 'application/x-pdf'
        # })

        mail_vals = {
            'model': 'account.move',
            'res_id': self.id,
            'email_from': email_from,
            'email_to': mail_to,
            'subject': subject,
            'body_html': 'This is an automatic message'}

        mail = self.env['mail.mail'].create(mail_vals)
        mail.attachment_ids = self.attachment_ids[0]
        self.env['mail.mail'].send([mail])


    def log_sent_to_accounttant(self):
        self.message_post(
            body='sent document to accounttant',
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            author_id=self.env.user.partner_id.id)
        self.sent_to_accounttant = True
                    
    