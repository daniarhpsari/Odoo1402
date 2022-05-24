from odoo import fields, models


class HrEmployeeType(models.Model):
    _name = "hr.employee.type"
    _description = "Employee Type"

    name = fields.Char('Name', required=True)
    sequence = fields.Integer('Sequence', default=10)


class HrContract(models.Model):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    employee_type_id = fields.Many2one(
        'hr.employee.type', string="Employee Type")
    resource_calendar_id = fields.Many2one(
        required=True, help="Employee's working schedule.")
    travel_allowance = fields.Monetary(
        string="Travel Allowance", help="Travel allowance")
    da = fields.Monetary(string="DA", help="Dearness allowance")
    meal_allowance = fields.Monetary(
        string="Meal Allowance", help="Meal allowance")
    medical_allowance = fields.Monetary(
        string="Medical Allowance", help="Medical allowance")
    other_allowance = fields.Monetary(
        string="Other Allowance", help="Other allowances")
    achievement_allowance = fields.Monetary(
        string="achievement Allowance", help="achievement allowance")
    attendance_allowance = fields.Monetary(
        string="attendance Allowance", help="Medical allowance")


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    employee_type_id = fields.Many2one(
        'hr.employee.type', string="Employee Type")
