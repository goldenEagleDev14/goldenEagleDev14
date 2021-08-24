from odoo import fields, api, models, _
from odoo import exceptions

from datetime import datetime, time

from dateutil import rrule
from odoo import fields, api, models, _
from odoo import exceptions

from datetime import datetime, time

from dateutil import rrule
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_available_contracts_domain(self):
        return [('company_id', '=', self.env.company.id)]

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    contract_valid_based = fields.Boolean(default=False,help="If this field is set the salary rule rate will be affected by the start and end dates of the contract.")

class HrContract(models.Model):
    _inherit = 'hr.contract'

    def get_work_ratio(self,date_from,date_to):
        # date_to =
        salary_start = max(self.date_start,date_from) if self.date_start else date_from
        salary_end = min(self.date_end,date_to) if self.date_end else date_to

        # This the case of normal payslip (month does not contain join date or contract end )
        if salary_start == date_from and salary_end == date_to:
            return 1

        salary_start_datetime = fields.Datetime.from_string(salary_start)
        salary_end_datetime = fields.Datetime.from_string(salary_end)
        month_days_count = 30
        month_end = fields.Datetime.from_string(date_to)
        month_start = fields.Datetime.from_string(date_from)

        payslip_days = (month_end - month_start).days + 1

        # The case of month contain contract end i.e. employee termination or resignation
        if salary_start == date_from:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1

        # The case of month contain join date i.e. first month for an employee (new employee)
        elif salary_end == date_to:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1


        # The case of employee that join and resigned on the same month
        else:
            num_work_days = (salary_end_datetime - salary_start_datetime).days + 1

        if salary_end == date_to:
            num_work_days = num_work_days + month_days_count - payslip_days
        print(num_work_days)
        return (1.0 * num_work_days) / (1.0 * month_days_count)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('worked_days_line_ids', 'input_line_ids')
    def _onchange_worked_days_inputs(self):
        # if self.line_ids and self.state in ['draft', 'verify']:
        #     values = [(5, 0, 0)] + [(0, 0, line_vals) for line_vals in self._get_payslip_lines()]
        #     self.update({'line_ids': values})
        print('ddddd')

    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id
        payslip = self.env['hr.payslip'].browse(self.id)


        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            # Modification here
            if rule.contract_valid_based:
                contract_rate = contract.get_work_ratio(payslip.date_from, payslip.date_to)
                localdict['result_rate'] = 100.0 * contract_rate
            # end modification
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                #check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                #set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()
