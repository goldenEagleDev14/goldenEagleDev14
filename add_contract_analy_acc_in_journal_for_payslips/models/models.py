# -*- coding: utf-8 -*-
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval

from odoo.tools import float_compare, float_is_zero


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    # def create_draft_entry_from_api(self,payslip):
    #     ret_db=self.env['db.credential'].search([],limit=1)
    #     if not ret_db:
    #         return None
    #     url = ret_db.server_url
    #     db = ret_db.db_name
    #     username = ret_db.db_user
    #     password = ret_db.db_password
    #
    #     common = xmlrpc_client.ServerProxy('{}/xmlrpc/2/common'.format(url)
    #                                        , verbose=False, use_datetime=True, context=ssl._create_unverified_context())
    #     uid = common.authenticate(db, username, password, {})
    #     models = xmlrpc_client.ServerProxy('{}/xmlrpc/2/object'.format(url), allow_none=True
    #                                        , verbose=False, use_datetime=True, context=ssl._create_unverified_context())
    #
    #     models.execute_kw(db, uid, password,
    #                                     'hr.payslip', 'call_action_payslip_done',
    #                                     [payslip.id])
    #     ##

    def action_validate(self):
        """
        in action_validate
       stop code and loop on payslips call custom action_payslip_done
       and get move linked for each payslip then get lines inside it

       loop to inc lines

       remove the moves

       create new one

        """

        for rec in self:
            batch_move_details = {}
            counter = 1
            move_lines = []
            for payslip in rec.slip_ids.filtered(lambda slip: slip.state != 'cancel'):
                # call payslip.action_payslip_done() from the api as looping on payslips
                # of batch and call create draft entry not create a move
                # but all payslips in batch has one move

                payslip.custom_action_payslip_done()
                move = payslip.move_id

                if counter == 1:
                    batch_move_details['ref'] = move.ref
                    # batch_move_details['review'] = move.review
                    batch_move_details['date'] = str(move.date)
                    batch_move_details['journal_id'] = move.journal_id.id
                    batch_move_details['company_id'] = move.company_id.id
                    batch_move_details['invoice_user_id'] = move.invoice_user_id.id
                    batch_move_details['team_id'] = move.team_id.id
                    batch_move_details['auto_post'] = move.auto_post

                for move_line in move.line_ids:
                    print('analytic_account_id',move_line.analytic_account_id.id)
                    move_lines.append(
                        {
                            'account_id': move_line.account_id.id,
                            'analytic_account_id': move_line.analytic_account_id.id,
                            'partner_id': move_line.partner_id.id,
                            'name': move_line.name,
                            'debit': move_line.debit,
                            'credit': move_line.credit,
                            # 'purchase_price':move_line.purchase_price,
                        })
                counter += 1
                move.unlink()

            # create new move as to be for the whole batch
            # with the all move lines of payslips

            # merge move lines #run if need merging with analytic account and account id
            # merged_move_lines=[]
            # for line in move_lines:
            #     merged=False
            #     for merged_move in merged_move_lines:
            #        if line['account_id'] == merged_move['account_id'] and line['analytic_account_id'] == merged_move['analytic_account_id']:
            #            if merged_move['debit']!=0 and line['debit']!=0:
            #                merged_move['debit']+=line['debit']
            #                merged = True
            #                break
            #            if merged_move['credit'] != 0 and line['credit']!=0:
            #                merged_move['credit']+=line['credit']
            #                merged=True
            #                break
            #     if merged:
            #         continue
            #
            #     else:
            #         merged_move_lines.append(line)

            # create move for batch
            batch_move_details['line_ids'] = [(0, 0, line_info) for line_info in
                                              move_lines]  # merged_move_lines if merged
            move_for_batch = self.env['account.move'].create(batch_move_details)
            for payslip in rec.slip_ids.filtered(lambda slip: slip.state == 'done'):
                payslip.move_id = move_for_batch.id
            rec.action_close()


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # @api.model
    # def call_action_payslip_done(self,payslip_id):
    #     payslip=self.env['hr.payslip'].search([('id','=',payslip_id)])
    #     if payslip:
    #         payslip.custom_action_payslip_done()
    #     return True

    def action_payslip_done_in_hr_payroll_account(self):
        ##
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        precision = self.env['decimal.precision'].precision_get('Payroll')

        # Add payslip without run
        payslips_to_post = self  # .filtered(lambda slip: not slip.payslip_run_id)

        # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
        payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
        for run in payslip_runs:
            if run._are_payslips_ready():
                payslips_to_post |= run.slip_ids

        # A payslip need to have a done state and not an accounting move.
        payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)

        # Check that a journal exists on all the structures
        if any(not payslip.struct_id for payslip in payslips_to_post):
            raise ValidationError(_('One of the contract for these payslips has no structure type.'))
        if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
            raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))

        # Map all payslips by structure journal and pay slips month.
        # {'journal_id': {'month': [slip_ids]}}
        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(slip.date_to, 'month'): self.env['hr.payslip']} for slip
            in payslips_to_post}
        for slip in payslips_to_post:
            slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip

        for journal_id in slip_mapped_data:  # For each journal_id.
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0
                date = slip_date
                move_dict = {
                    'narration': '',
                    'ref': date.strftime('%B %Y'),
                    'journal_id': journal_id,
                    'date': date,
                }

                for slip in slip_mapped_data[journal_id][slip_date]:
                    move_dict['narration'] += slip.number or '' + ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    for line in slip.line_ids.filtered(lambda line: line.category_id):
                        amount = -line.total if slip.credit_note else line.total
                        if line.code == 'NET':  # Check if the line is the 'Net Salary'.
                            for tmp_line in slip.line_ids.filtered(lambda line: line.category_id):
                                if tmp_line.salary_rule_id.not_computed_in_net:  # Check if the rule must be computed in the 'Net Salary' or not.
                                    if amount > 0:
                                        amount -= abs(tmp_line.total)
                                    elif amount < 0:
                                        amount += abs(tmp_line.total)
                        if float_is_zero(amount, precision_digits=precision):
                            continue
                        debit_account_id = line.salary_rule_id.account_debit.id
                        credit_account_id = line.salary_rule_id.account_credit.id

                        if debit_account_id:  # If the rule has a debit account.
                            debit = amount if amount > 0.0 else 0.0
                            credit = -amount if amount < 0.0 else 0.0

                            existing_debit_lines = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == debit_account_id
                                and line_id['analytic_account_id'] == (
                                        line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id)
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
                            debit_line = next(existing_debit_lines, False)

                            if not debit_line:
                                debit_line = {
                                    'name': line.name,
                                    'partner_id': slip.employee_id.address_id.id,
                                    'account_id': debit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(debit_line)
                            else:
                                debit_line['debit'] += debit
                                debit_line['credit'] += credit

                        if credit_account_id:  # If the rule has a credit account.
                            debit = -amount if amount < 0.0 else 0.0
                            credit = amount if amount > 0.0 else 0.0
                            existing_credit_line = (
                                line_id for line_id in line_ids if
                                line_id['name'] == line.name
                                and line_id['account_id'] == credit_account_id
                                and line_id['analytic_account_id'] == (
                                        line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id)
                                and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0))
                            )
                            credit_line = next(existing_credit_line, False)

                            if not credit_line:
                                credit_line = {
                                    'name': line.name,
                                    'partner_id': slip.employee_id.address_id.id,
                                    'account_id': credit_account_id,
                                    'journal_id': slip.struct_id.journal_id.id,
                                    'date': date,
                                    'debit': debit,
                                    'credit': credit,
                                    'analytic_account_id': line.salary_rule_id.analytic_account_id.id or slip.contract_id.analytic_account_id.id,
                                }
                                line_ids.append(credit_line)
                            else:
                                credit_line['debit'] += debit
                                credit_line['credit'] += credit

                for line_id in line_ids:  # Get the debit and credit sum.
                    debit_sum += line_id['debit']
                    credit_sum += line_id['credit']

                # The code below is called if there is an error in the balance between credit and debit sum.
                if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_credit_account_id.id
                    if not acc_id:
                        raise UserError(
                            _('The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_credit = next(existing_adjustment_line, False)

                    if not adjust_credit:
                        adjust_credit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': 0.0,
                            'credit': debit_sum - credit_sum,
                        }
                        line_ids.append(adjust_credit)
                    else:
                        adjust_credit['credit'] = debit_sum - credit_sum

                elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
                    acc_id = slip.journal_id.default_debit_account_id.id
                    if not acc_id:
                        raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (
                            slip.journal_id.name))
                    existing_adjustment_line = (
                        line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
                    )
                    adjust_debit = next(existing_adjustment_line, False)

                    if not adjust_debit:
                        adjust_debit = {
                            'name': _('Adjustment Entry'),
                            'partner_id': False,
                            'account_id': acc_id,
                            'journal_id': slip.journal_id.id,
                            'date': date,
                            'debit': credit_sum - debit_sum,
                            'credit': 0.0,
                        }
                        line_ids.append(adjust_debit)
                    else:
                        adjust_debit['debit'] = credit_sum - debit_sum

                # Add accounting lines in the move
                move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
                move = self.env['account.move'].create(move_dict)
                for slip in slip_mapped_data[journal_id][slip_date]:
                    slip.write({'move_id': move.id, 'date': date})

        ##

    def action_payslip_done_in_hr_payroll(self):
        ##
        if any(slip.state == 'cancel' for slip in self):
            raise ValidationError(_("You can't validate a cancelled payslip."))
        self.write({'state': 'done'})
        self.mapped('payslip_run_id').action_close()
        if self.env.context.get('payslip_generate_pdf'):
            for payslip in self:
                if not payslip.struct_id or not payslip.struct_id.report_id:
                    report = self.env.ref('hr_payroll.action_report_payslip', False)
                else:
                    report = payslip.struct_id.report_id
                pdf_content, content_type = report.render_qweb_pdf(payslip.id)
                if payslip.struct_id.report_id.print_report_name:
                    pdf_name = safe_eval(payslip.struct_id.report_id.print_report_name, {'object': payslip})
                else:
                    pdf_name = _("Payslip")
                self.env['ir.attachment'].create({
                    'name': pdf_name,
                    'type': 'binary',
                    'datas': base64.encodestring(pdf_content),
                    'res_model': payslip._name,
                    'res_id': payslip.id
                })

        ##

    # to be called  from the payslip batch when press crate draft entry
    # to create moves for payslips,then merge them in one move
    def custom_action_payslip_done(self):
        # make it as the functions named action_payslip_done in hr_payroll and hr_payrol_account
        res = self.action_payslip_done_in_hr_payroll()
        # action_payslip_done in hr_payroll
        ##action_payslip_done in hr_payroll_account
        self.action_payslip_done_in_hr_payroll_account()

        ##chanage the analytic account to the one in contract
        ##
        # for slip in self:
        #     # slip.write({'move_id': move.id, 'date': date})
        #     if slip.employee_id.contract_id and slip.employee_id.contract_id.analytic_account_id:
        #         analytic_account_in_contract = slip.employee_id.contract_id.analytic_account_id.id
        #         # change analytic account in move lines
        #         if slip.move_id:
        #             for rec in slip.move_id.line_ids:
        #                 rec.write({
        #                     # 'analytic_account_id': analytic_account_in_contract,
        #                     'partner_id': slip.employee_id.address_id.id,
        #                 })

        ##
        ##
        return res

    # for create draft entry from a payslip,
    # it's set analtic account of contratc on the journal entry
    def action_payslip_done(self):
        """
            Generate the accounting entries related to the selected payslips
            A move is created for each journal and for each month.
        """
        res = super(HrPayslip, self).action_payslip_done()

        ##
        for slip in self:
            # slip.write({'move_id': move.id, 'date': date})
            if slip.employee_id.contract_id and slip.employee_id.contract_id.analytic_account_id:
                analytic_account_in_contract = slip.employee_id.contract_id.analytic_account_id.id
                # change analytic account in move lines
                if slip.move_id:
                    slip.move_id.ref = slip.number
                    for rec in slip.move_id.line_ids:
                        rec.write({
                            # 'analytic_account_id':analytic_account_in_contract,
                            'partner_id': slip.employee_id.address_id.id,
                        })

            for slip in self:
                # slip.write({'move_id': move.id, 'date': date})
                if slip.employee_id.contract_id and slip.employee_id.contract_id.analytic_account_id:
                    analytic_account_in_contract = slip.employee_id.contract_id.analytic_account_id.id
                    # change analytic account in move lines
                    if slip.move_id:
                        for rec in slip.move_id.line_ids:
                            rec.write({
                                'analytic_account_id':analytic_account_in_contract,
                                # 'partner_id': slip.employee_id.address_id.id,
                            })

            analytic_account_in_contract = slip.employee_id.contract_id
        ##
        return res
