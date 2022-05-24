from typing import Sequence
from odoo import models, fields, api
from ast import literal_eval

PromotionCode = [
    ('internal', 'Internal Company'),
    ('external', 'Transfer Inter Company')
]


class HrPromoteType(models.Model):
    _name = "hr.promote.type"
    _description = "Promotion Type"

    name = fields.Char('Name', required=True)
    code = fields.Char('Short name', required=True)
    color = fields.Integer('Color')
    sequence = fields.Integer('Sequence', default=10)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence Table', default=10)
    type = fields.Selection(PromotionCode, 'Type', help="""Promotion code
        1. Internal Transfer same company
            for example: employee in company a have job staff IT and you promote this employee to CTO in same company
        2. Transfer Inter Company
            for example: employee in company a and you mutation this employee to company B.""",
                            default='internal', groups="hr.group_hr_manager")
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    count_promote_draft = fields.Integer(compute='_compute_promotion')
    count_promote_confirm = fields.Integer(compute='_compute_promotion')
    count_promote_to_start = fields.Integer(compute='_compute_promotion')

    _sql_constraints = [
        ('unique_code', 'unique(code)',
         'This Short name is already exits.'),
    ]

    @api.model
    def create(self, vals):
        ir_sequence = self.env['ir.sequence'].create({
            'name': vals['name'],
            'code': vals['name'].replace(" ", "_"),
            'prefix': vals['code']+'/%(year)s/',
            'padding': 5,
            'company_id': self.company_id.id,
            'use_date_range': True,
        })
        vals['sequence_id'] = ir_sequence.id
        value = super(HrPromoteType, self).create(vals)
        return value

    def _compute_promotion(self):
        domains = {
            'count_promote_draft': [('state', '=', 'draft')],
            'count_promote_confirm': [('state', '=', 'confirm')],
            'count_promote_to_start': [('state', '=', 'waiting')],
        }
        for field in domains:
            data = self.env['hr.promotion'].read_group(domains[field] +
                                                       [('state', 'not in', ('cancel', 'done')),
                                                        ('type_id', 'in', self.ids)],
                                                       ['type_id'], ['type_id'])

            count = {
                x['type_id'][0]: x['type_id_count']
                for x in data if x['type_id']
            }
            for record in self:
                record[field] = count.get(record.id, 0)

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.name
        context = {
            'search_default_type_id': [self.id],
            'default_type_id': self.id,
            'default_code': self.type,
            'default_company_id': self.company_id.id,
        }
        domain = [('code', '=', self.type)]

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = domain
        return action

    def get_action_promote_tree_ready(self):
        return self._get_action('hr_promote.hr_promote_action_ready')

    def get_action_promote_tree_waiting(self):
        return self._get_action('hr_promote.hr_promote_action_waiting')

    def get_action_promote_tree_to_start(self):
        return self._get_action('hr_promote.hr_promote_action_to_start')

    def get_action_promote_type(self):
        return self._get_action('hr_promote.hr_promote_action')

    def get_action_promote_form(self):
        return self._get_action('hr_promote.action_promote_form')


class HrPromoteCC(models.Model):
    _name = "hr.cc"
    _description = "Employee cc"

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
