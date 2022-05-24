from odoo import models, fields, api, _
from datetime import date

PromotionCode = [
    ('internal', 'Internal Company'),
    ('external', 'Transfer Inter Company')
]


class HrWarningNotice(models.Model):
    _name = "hr.promotion"
    _description = "Employee Promotion"
    _inherit = ['mail.thread',
                'mail.activity.mixin']

    name = fields.Char('name', required=True, copy=False, readonly=True, states={
                       'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    date = fields.Datetime('Date', required=True, readonly=True, states={
        'draft': [('readonly', False)]}, tracking=True, default=fields.Datetime.now)
    start_date = fields.Date('Start Date', required=True, tracking=True)
    type_id = fields.Many2one(
        'hr.promote.type', 'Type', tracking=True, required=True, readonly=True, states={
            'draft': [('readonly', False)]}, domain="[('type', '=?', code)]")
    code = fields.Selection(
        PromotionCode, string="Code")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting', 'To Start'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", required=True, readonly=True, states={'draft': [('readonly', False)]}, tracking=True)
    employee_type_id = fields.Many2one(
        'hr.employee.type', string="Employee Type", readonly=True, store=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    transfer_company_id = fields.Many2one(
        'res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(
        string="Currency", related='company_id.currency_id', readonly=True)
    department_id = fields.Many2one(
        'hr.department', string="Department", store=True)
    job_id = fields.Many2one(
        'hr.job', string="Job Position", store=True)
    parent_id = fields.Many2one(
        'hr.employee', 'Manager', store=True)
    coach_id = fields.Many2one(
        'hr.employee', 'Coach', store=True)
    contract_id = fields.Many2one('hr.contract')
    resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Hours', related="contract_id.resource_calendar_id")
    wage_salary = fields.Monetary(
        related='contract_id.wage', required=True, tracking=True, help="Employee's monthly gross wage.")
    da = fields.Monetary(related='contract_id.da')
    achievement_allowance = fields.Monetary(
        related='contract_id.achievement_allowance')
    attendance_allowance = fields.Monetary(
        related='contract_id.attendance_allowance')
    travel_allowance = fields.Monetary(
        related='contract_id.travel_allowance', help="Travel allowance")
    meal_allowance = fields.Monetary(
        related='contract_id.meal_allowance', help="Meal allowance")
    medical_allowance = fields.Monetary(
        related='contract_id.medical_allowance', help="Medical allowance")
    other_allowance = fields.Monetary(
        related='contract_id.other_allowance', help="Other allowances")
    new_contract_id = fields.Many2one('hr.contract')
    new_employee_type_id = fields.Many2one(
        'hr.employee.type', string="Employee Type", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_department_id = fields.Many2one(
        'hr.department', string="Department", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_job_id = fields.Many2one(
        'hr.job', string="New Job Position", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_wage_salary = fields.Monetary(
        'Wage', required=True, tracking=True, help="Employee's monthly gross wage.", readonly=True, states={
            'draft': [('readonly', False)]})
    new_achievement_allowance = fields.Monetary(
        string="Achievement Allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_attendance_allowance = fields.Monetary(
        string="Attendance Allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_travel_allowance = fields.Monetary(
        string="Travel Allowance", help="Travel allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_da = fields.Monetary(
        string="DA", help="Dearness allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_meal_allowance = fields.Monetary(
        string="Meal Allowance", help="Meal allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_medical_allowance = fields.Monetary(
        string="Medical Allowance", help="Medical allowance", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    new_other_allowance = fields.Monetary(
        string="Other Allowance", help="Other allowances", tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    hr_staff_uid = fields.Many2one(
        'res.users', string='HR Responsible', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('hr.group_hr_user').id)])
    hr_staff_signature = fields.Image(
        string="HR Staff Signature", max_width=1024, max_height=1024, readonly=True, copy=False)
    new_parent_id = fields.Many2one('hr.employee', 'Manager', tracking=True, readonly=True, states={
        'draft': [('readonly', False)]})
    new_coach_id = fields.Many2one('hr.employee', 'Coach', tracking=True, readonly=True, states={
        'draft': [('readonly', False)]})
    new_resource_calendar_id = fields.Many2one(
        'resource.calendar', 'Working Hours', required=True, tracking=True, readonly=True, states={
            'draft': [('readonly', False)]})
    note = fields.Char('Note', readonly=True, states={
                       'draft': [('readonly', False)]})
    cc_ids = fields.Many2many('hr.cc', 'promotion_id', 'cc_id', string='cc',
                              help="the name of the department or manager that is a copy of the warning")

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.department_id = self.employee_id.department_id
        self.job_id = self.employee_id.job_id
        self.employee_type_id = self.employee_id.employee_type_id
        self.contract_id = self.employee_id.contract_id
        self.parent_id = self.employee_id.parent_id
        self.coach_id = self.employee_id.coach_id

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
            if 'warning_date' in vals:
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['warning_date']))
            type_id = self.env['hr.promote.type'].search(
                [('id', '=', vals['type_id'])])
            vals['name'] = type_id.sequence_id.next_by_id(
                sequence_date=seq_date) or _('New')
        result = super(HrWarningNotice, self).create(vals)
        return result

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def _waiting_state(self):
        return self.write({'state': 'waiting'})

    def action_validate(self):
        return {'type': 'ir.actions.act_window',
                'name': _('User Signature'),
                'res_model': 'hr.promote.signature',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                        'default_user_id': self.hr_staff_uid.id,
                        'default_promote_id': self.id
                },
                }

    def _action_validate(self):
        if self.start_date == date.today():
            self.update_employee_information()
        else:
            self._waiting_state()

    def update_employee_information(self):
        data = self.prepare_employee_information()
        if self.code == 'external':
            data['company_id'] = self.transfer_company_id.id
        self.contract_id.state = 'cancel'
        self.contract_id.kanban_state = 'done'
        self.employee_id.write(data)
        self.create_new_contract()
        self.action_done()

    def prepare_employee_information(self):
        return {
            'department_id': self.new_department_id.id,
            'job_id': self.new_job_id.id,
            'employee_type_id': self.new_employee_type_id.id,
            'parent_id': self.new_parent_id.id,
            'coach_id': self.new_coach_id.id,
            'resource_calendar_id': self.new_resource_calendar_id.id,
        }

    def create_new_contract(self):
        data = self.prepare_contract_information()
        if self.code == 'internal':
            contract = self.sudo().new_contract_id.create(data)
            self.sudo().new_contract_id = contract.id
            self.sudo().new_contract_id.state = 'open'
            self.sudo().contract_id.kanban_state = 'done'

    def action_send_letter(self):
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'hr.promotion',
            'default_res_id': self.ids[0],
            'default_parent_ids': self.employee_id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False
        template_id = int(self.env['ir.config_parameter'].sudo(
        ).get_param('hr_promote.default_promote_template'))
        template_id = self.env['mail.template'].search(
            [('id', '=', template_id)]).id
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id(
                'hr_promote.email_template_promote', raise_if_not_found=False)

        return template_id

    def prepare_contract_information(self):
        return {
            'name': '%s Contract' % self.employee_id.name,
            'employee_id': self.employee_id.id,
            'department_id': self.new_department_id.id,
            'job_id': self.new_job_id.id,
            'company_id': self.company_id.id,
            'employee_type_id': self.new_employee_type_id.id,
            'date_start': self.start_date,
            'resource_calendar_id': self.new_resource_calendar_id.id,
            'wage': self.new_wage_salary,
            'travel_allowance': self.new_travel_allowance,
            'da': self.new_da,
            'meal_allowance': self.new_meal_allowance,
            'medical_allowance': self.new_medical_allowance,
            'other_allowance': self.new_other_allowance,
            'achievement_allowance': self.new_achievement_allowance,
            'attendance_allowance': self.new_attendance_allowance
        }

    def update_state(self):
        print('______Cron Job______')
        datas = self.search([
            ('state', '=', 'waiting'),
            ('start_date', '=', date.today()),
        ])
        for data in datas:
            data.update_employee_information()

    def action_done(self):
        return self.write({'state': 'done'})

    def action_draft(self):
        return self.write({'state': 'draft'})
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hr_promote_template_id = fields.Many2one('mail.template', string='Promote Email',
                                                 domain="[('model', '=', 'hr.promotion')]",
                                                 config_parameter='hr_promote.default_promote_template',
                                                 help="Email sent to the employee once the Promote.")
