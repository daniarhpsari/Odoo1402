# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd
#    (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api
from datetime import datetime


class JobPositionRequest(models.Model):
    _name = "job.position.request"
    _description = "Create new job positions from here"

    def make_url(self):
        menu_id = self.env.ref("dev_job_position_request.menu_job_position_request").id
        action_id = self.env.ref("dev_job_position_request.action_dev_job_position_request").id
        ir_param = self.env['ir.config_parameter'].sudo()
        base_url = ir_param.get_param('web.base.url')
        if base_url:
            base_url += '/web#id=%s&action=%s&model=%s&view_type=form&cids=&menu_id=%s' % (self.id, action_id, self._name, menu_id)
        return base_url

    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('job.position.request.sequence') or 'New'
        return super(JobPositionRequest, self).create(vals)

    @api.returns('self')
    def _get_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1) or False

    def submit_to_manager(self):
        self.state = "to approve"
        if not self.env.user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            authorized_group = self.env.ref('hr_recruitment.group_hr_recruitment_manager')
            if authorized_group and authorized_group.users:
                authorized_users = authorized_group.users
                email_from = self.env.user and self.env.user.partner_id and self.env.user.partner_id.email or ''
                template = self.env.ref("dev_job_position_request.email_template_job_position_request")
                if template and email_from and authorized_users:
                    template_id = self.env['mail.template'].browse(int(template))
                    if template_id:
                        for user in authorized_users:
                            if user.partner_id and user.partner_id.email:
                                template_id.write({'email_from': email_from})
                                template_id.write({'email_to': user.partner_id.email})
                                template_id.send_mail(self.id, force_send=True)

    def send_job_position_created_email(self, job_id):
        if self.job_id and self.employee_id:
            if self.employee_id.user_id and self.employee_id.user_id.partner_id and self.employee_id.user_id.partner_id.email:
                if self.env.user and self.env.user.partner_id and self.env.user.partner_id.email:
                    template = self.env.ref("dev_job_position_request.template_manger_to_user")
                    if template:
                        template_id = self.env['mail.template'].browse(int(template))
                        if template_id:
                            template_id.write({'email_from': self.env.user.partner_id.email})
                            template_id.write({'email_to': self.employee_id.user_id.partner_id.email})
                            template_id.send_mail(self.id, force_send=True)

    def send_job_position_rejected_email(self):
        if self.employee_id.user_id and self.employee_id.user_id.partner_id and self.employee_id.user_id.partner_id.email:
            if self.env.user and self.env.user.partner_id and self.env.user.partner_id.email:
                template = self.env.ref("dev_job_position_request.email_template_job_position_request_rejected")
                if template:
                    template_id = self.env['mail.template'].browse(int(template))
                    if template_id:
                        template_id.write({'email_from': self.env.user.partner_id.email})
                        template_id.write({'email_to': self.employee_id.user_id.partner_id.email})
                        template_id.send_mail(self.id, force_send=True)

    def approve_request(self):
        self.state = "approved"

    def reject_request(self):
        self.state = "rejected"
        if self.employee_id and self.employee_id.user_id:
            if self.env.user.id == self.employee_id.user_id.id:
                pass
            else:
                self.send_job_position_rejected_email()
        else:
            self.send_job_position_rejected_email()

    def set_to_new(self):
        self.state = "new"

    def view_job_position(self):
        form_id = self.env.ref("hr.view_hr_job_form").id
        return {'name': 'Job Position',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.job',
                'views': [(form_id, 'form')],
                'target': 'current',
                'res_id': self.job_id.id
                }

    def create_new_job_position(self):
        job_id = self.env['hr.job'].create({'name': self.name,
                                            'description': self.description,
                                            'department_id': self.department_id and self.department_id.id or False,
                                            'no_of_recruitment': self.expected_new_employees,
                                            'state': 'recruit',
                                            'hr_responsible_id': self.env.user.id or False,
                                            'user_id': self.env.user.id or False
                                            })
        if job_id:
            self.job_id = job_id.id or False
            self.state = 'job_position_created'
            if self.employee_id and self.employee_id.user_id:
                if self.env.user.id == self.employee_id.user_id.id:
                    pass
                else:
                    self.send_job_position_created_email(job_id)
            else:
                self.send_job_position_created_email(job_id)

    def job_position_details(self):
        position_details = '''<table border=1 width=40% style="border-collapse: collapse;">'''
        tr_start = '''<tr>'''
        tr_end = '''</tr>'''
        td_start = '''<td>'''
        td_end = '''</td>'''
        th_end = '''</th>'''
        colspan_th_start = '''<th colspan=2 style="text-align: center";>'''
        colspan_th_start2 = '''<th style="text-align: left;">'''
        colspan_th_end = '''</th>'''
        position_details += tr_start + colspan_th_start + str(self.name) + colspan_th_end + tr_end
        date = datetime.strptime(str(self.date), "%Y-%m-%d").strftime('%d-%m-%Y')
        position_details += tr_start + colspan_th_start2 + 'Requested On' + th_end
        position_details += td_start + str(date) + td_end + tr_end + tr_end
        position_details += tr_start + colspan_th_start2 + 'Requested by' + th_end
        position_details += td_start + str(self.employee_id.name) + td_end + tr_end
        position_details += tr_start + colspan_th_start2 + 'Employees Required' + th_end
        position_details += td_start + str(self.expected_new_employees) + td_end + tr_end
        position_details += '''</table>'''
        return position_details

    name = fields.Char(string="Job Position", required=True)
    sequence = fields.Char(string="Sequence", copy=False, readonly=1)
    employee_id = fields.Many2one("hr.employee", string="Requested By", default=_get_employee, readonly=1)
    department_id = fields.Many2one("hr.department", string="Department")
    expected_new_employees = fields.Integer(string="Expected New Employees", required=1)
    date = fields.Date(string="Requested On", required=1)
    job_id = fields.Many2one("hr.job", string="Job Position", copy=False)
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.user.company_id, copy=False)
    description = fields.Text(string="Description")
    state = fields.Selection(selection=[('new', 'New'),
                                        ('to approve', 'To Approve'),
                                        ('approved', 'Approved'),
                                        ('job_position_created', 'Job Position Created'),
                                        ('rejected', 'Rejected'),
                                        ], default='new', string="State")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
