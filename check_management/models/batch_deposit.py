from odoo import api, fields, models,_

from odoo.exceptions import UserError, ValidationError


class BatchDepositChecks(models.Model):
    _inherit = 'account.batch.payment'

    def _get_defualt_batch(self):
        payment_method_obj = self.env['account.payment.method']
        payment  = payment_method_obj.search([('name','not ilike','Manu')],limit=1)
        if payment:
            return payment.id

    bank_id = fields.Many2one(comodel_name='account.journal')

    state = fields.Selection(
        [('draft', 'New'), ('under_collection', 'Under collection'), ('sent', 'Printed'), ('reconciled', 'Reconciled'),
         ('discount', 'Discount'), ('loan', 'Loan'), ('done', 'Done')], readonly=True, default='draft', copy=False)
    read_only = fields.Boolean()
    deposite_move_type = fields.Selection([('discount', 'Discount')
                                              , ('other', 'Other')],
                                          default=lambda self: self.get_default_type_value())
    payment_ids_rel = fields.One2many('account.payment', 'batch_payment_id', string="Payments", required=True,
                                      readonly=True, states={'draft': [('readonly', False)]})

    payment_method_id = fields.Many2one(comodel_name='account.payment.method', string='Payment Method', 
    required=True, readonly=True, 
    states={'draft': [('readonly', '=', False)]},
    default = _get_defualt_batch,
     help="The payment method used by the payments in this batch.")

    @api.constrains('batch_type', 'journal_id', 'payment_ids')
    def _check_payments_constrains(self):
        for record in self:
            all_companies = set(record.payment_ids.mapped('company_id'))
            if len(all_companies) > 1:
                raise ValidationError(_("All payments in the batch must belong to the same company."))
            all_journals = set(record.payment_ids.mapped('journal_id'))
            if len(record.payment_ids) == 0:
                raise ValidationError(_("You must select atleast one payment."))
            if len(all_journals) > 1 or record.payment_ids[0].journal_id != record.journal_id:
                raise ValidationError(_("The journal of the batch payment and of the payments it contains must be the same."))
            all_types = set(record.payment_ids.mapped('payment_type'))
            if all_types and record.batch_type not in all_types:
                raise ValidationError(_("The batch must have the same type as the payments it contains."))
            all_payment_methods = set(record.payment_ids.mapped('payment_method_id'))
            if len(all_payment_methods) > 1:
                raise ValidationError(_("All payments in the batch must share the same payment method."))
            if all_payment_methods and record.payment_method_id not in all_payment_methods:
                raise ValidationError(_("The batch must have the same payment method as the payments it contains."))

    def draft(self):
        self.state = 'draft'
    #@api.multi
    def related_journal_button(self):
        return {
            'name': 'Journal Items',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.payment_ids.ids)],
            'context': {'group_by': ['payment_id']}
        }

    # counter for validation message in discount check
    #@api.multi
    def refund_under_collections(self):
        for rec in self:
            run = False
            for r in rec.payment_ids:
                if r.multi_select == True and r.state == 'under_coll':
                    run = True
                    r.refund_notes()
                    # r.refund_under_collection_date = r.ref_coll_batch
                    r.multi_select = False
            if not run:
                raise ValidationError("please select any check to refund it")
            if rec.change_state_refunded_and_collect():
                rec.write({'state': 'done'})
            if rec.change_state_refunded():
                rec.write({'state': 'done'})

    def get_default_type_value(self):

        ctx = self.env.context
        if 'is_discount_check_type' in ctx:
            return 'discount'
        elif 'is_other_check_type' in ctx:
            return 'other'

    #@api.multi
    def print_batch_deposit(self):
        # for deposit in self:
        #     if deposit.state != 'draft':
        #         continue
        #     deposit.payment_ids.write({'state': 'sent', 'payment_reference': deposit.name})
        #     deposit.write({'state': 'sent'})
        return self.env.ref('account_batch_payment.action_print_batch_deposit').report_action(self)

    #@api.one
    @api.constrains('journal_id', 'payment_ids')
    def _check_same_journal(self):
        if not self.journal_id:
            return
        if any(payment.journal_id != self.journal_id for payment in self.payment_ids):
            return

            # receive checks part start

    #@api.multi
    def post_bank_entrie(self):
        for rec in self:
            collect = False
            for r in rec.payment_ids:
                if r.multi_select == True and r.state != 'collected':
                    if not r.ref_coll_batch:
                        raise ValidationError('Please enter collect Date')
                    r._compute_destination_account_id()
                    r.post()
                    collect = True
                    r.multi_select = False
            if not collect:
                raise ValidationError("please select any check to collect it")
            if rec.change_state_refunded_and_collect():
                rec.write({'state': 'done'})
            if rec.change_state_collect():
                rec.write({'state': 'done'})

    #@api.multi
    def post_under_collection(self):
        for r in self.payment_ids:

            if r.state == 'posted' or r.state == 'refunded_under_collection':
                r.post()
                
                r.multi_select = False
                r.ref_coll_batch = False
        self.read_only = 'under_collection'
        self.state = 'under_collection'
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>AFTER POST",)
        # 1/0

    def change_state_collect(self):
        for r in self.payment_ids:
            if r.state != "collected":
                return False
        return True

    def change_state_refunded(self):
        for r in self.payment_ids:
            if r.state != "collected":
                return False
        return True

    def change_state_refunded_and_collect(self):
        for r in self.payment_ids:
            if r.state != "collected":
                if r.state != "refunded_under_collection":
                    return False
        return True
        # receive checks part end


        # discount checks part start

    def create_wizard_object(self, line):

        avaliable_pool = self.available_pool_validation_message(line=line)

        percentage_partner = self.partner_percentage_pool(line=line)
        tim_min = self.time_min_limit()
        tim_max = self.time_max_limit()
        if self.bank_id.bank_id.is_warning:
            part_perc = aval_pool = tm_min = tm_mx = False
            value = {'pool_exceed': "",
                     'min_limit': "",
                     'max_limit': '',
                     'centeral_percentage': ''}
            if percentage_partner:
                value['centeral_percentage'] += percentage_partner
                part_perc = True
            if avaliable_pool:
                value['pool_exceed'] += avaliable_pool
                aval_pool = True
            if tim_min:
                value['min_limit'] += tim_min
                tm_min = True
            if tim_max:
                value['max_limit'] += tim_max
                tm_mx = True
            if part_perc or aval_pool or tm_min or tm_mx:
                obj = self.env['warning.discount.wizard'].create(value)
                return obj
            return False
        else:

            warning_msg = ""

            if percentage_partner:
                warning_msg += percentage_partner
            if avaliable_pool:
                warning_msg += avaliable_pool
            if tim_min:
                warning_msg += tim_min
            if tim_max:
                warning_msg += tim_max
            if len(warning_msg) > 1:
                return warning_msg
            else:
                return False

    def discount_all(self):
        obj = from_wizard = False
        if 'force_discount_wizard' in self._context: from_wizard = self._context['force_discount_wizard']

        if self.state == 'draft':
            obj = self.create_wizard_object(False)

            if from_wizard:
                for r in self.payment_ids:
                    if r.state in ['posted', 'refund_from_discount', 'refunded_under_collection']:
                        r.with_context(discount_check=True).post()
                        r.multi_select = False


            elif obj and not type(obj) is str:
                if obj:
                    return {
                        'name': (
                            'hello this is a Warning message , please read carfuly the message before validate the transaction'),
                        'type': 'ir.actions.act_window',
                        'res_model': 'warning.discount.wizard',
                        'res_id': obj.id,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new'
                    }

            else:
                for r in self.payment_ids:
                    if r.state in ['posted', 'refund_from_discount', 'refunded_under_collection']:

                        if self.partner_percentage_pool(r):
                            # raise ValidationError(self.partner_percentage_pool(r))
                            message = self.create_wizard_object(r)
                            raise ValidationError(
                                "you can't accept this operations for those reasons\n{}".format(message))

                        if self.available_pool_validation_message(r):
                            # raise ValidationError(self.available_pool_validation_message(r))
                            message = self.create_wizard_object(r)
                            raise ValidationError(
                                "you can't accept this operations for those reasons\n{}".format(message))

                        r.post()
                        r.multi_select = False

            if self.change_discount_states('discount'):
                self.write({'state': 'discount'})

    def receive_all(self):
        no_select = True
        change_to_done = True
        for r in self.payment_ids:

            if r.state not in ['discount', 'refund_from_discount'] and r.multi_select:
                raise ValidationError(
                    'you try to loan check number {} and it\'s not in discount or refunded from discount stages'.format(
                        r.check_number))
            if r.state == 'loan':
                raise ValidationError(
                    'you try to loan check number {} and it\'s already loaned'.format(
                        r.check_number))

            if not r.loan_date and r.multi_select:
                raise ValidationError('please enter loan date for check number {}'.format(r.check_number))
            if r.state == 'discount' and r.multi_select:
                r.post()
                r.multi_select = False
                no_select = False
            if r.multi_select:
                no_select = False
            if r.state not in ['collected', 'refund_from_discount']:
                change_to_done = False
        if change_to_done:
            self.write({'state': 'done'})
        if no_select:
            raise ValidationError('make sure that you select one check at least')

    def refund_discount(self):
        for rec in self:
            change_to_done = True
            no_selection = True
            for r in rec.payment_ids:

                if r.state != 'loan' and r.multi_select:
                    raise ValidationError(
                        'you try to refund check number {} and it\'s not in loan stage'.format(r.check_number))

                if not r.ref_coll_batch and r.multi_select:
                    raise ValidationError(
                        'please enter [Refund/collect] date for check number {}'.format(r.check_number))

                if r.multi_select == True and r.state in ['loan', 'discount']:
                    r.refund_discount()
                    r.multi_select = False
                    no_selection = False

                if r.state not in ['collected', 'refund_from_discount']:
                    change_to_done = False
            if no_selection:
                raise ValidationError('make sure that you select one check at least')
            if change_to_done:
                rec.write({'state': 'done'})

                # if rec.change_state_refunded_and_collect():
                #     rec.write({'state': 'done'})
                # if rec.change_state_refunded():
                #     rec.write({'state': 'done'})

    def collect_discount(self):
        no_selection = True
        for r in self.payment_ids:

            if r.state == 'collected' and r.multi_select:
                raise ValidationError(
                    'you try to collect check number {} and it\'s already collected'.format(
                        r.check_number))
            if r.state != 'loan' and r.multi_select:
                raise ValidationError(
                    'you try to collect check number {} and it\'s not in loan stage'.format(r.check_number))

            if not r.ref_coll_batch and r.multi_select:
                raise ValidationError('please enter [Refund/collect] date for check number {}'.format(r.check_number))

            if r.state == 'loan' and r.multi_select:
                r.post()
                r.multi_select = False
                no_selection = False

        if no_selection:
            raise ValidationError('make sure that you select one check at least')

        if self.change_discount_states('collected'):
            self.write({'state': 'done'})

    def change_discount_states(self, state_name):
        for r in self.payment_ids:
            if r.state != state_name:
                return False
        return True

    def partner_percentage_pool(self, line):
        loan_account = self.bank_id.loan_account.id
        discount_check = self.bank_id.discount_check_account.id
        max_available = (self.bank_id.bank_id.central_percentage / 100) * self.bank_id.bank_id.available_pool
        used = 0
        msg = ""

        if line:
            aml_c = self.env['account.move.line'].search(
                [('partner_id', '=', line.partner_id.id), ('credit', '>', 0), ('account_id', '=', loan_account)])
            aml_d = self.env['account.move.line'].search(
                [('partner_id', '=', line.partner_id.id), ('debit', '>', 0), ('account_id', '=', loan_account)])
            credit, debit = 0, 0
            if aml_c:
                for r in aml_c:
                    credit += r.credit
            if aml_d:
                for r in aml_d:
                    debit += r.debit
            # if aml_c: credit = aml_c.credit
            # if aml_d: debit = aml_d.debit
            used += credit - debit
            discount_percentage = line.amount / 100 * self.bank_id.bank_id.loan_percentage
            used_with_amount = used + discount_percentage

            if max_available < used_with_amount:
                msg += "- amount for check Number ({}) to partner ({}) is exceed the central percentage in bank ({}) \n".format(
                    line.check_number, line.partner_id.name, self.bank_id.bank_id.name)
            if len(msg) > 2:
                return msg
            else:
                False
        else:

            partner = set([r.partner_id for r in self.payment_ids])

            for p in partner:
                check_numbers = ""
                used_with_amount = 0
                total_amount = 0
                exceed = False
                used = 0

                for r in self.payment_ids:
                    if r.partner_id.id != p.id:
                        continue
                    aml_c = self.env['account.move.line'].search(
                        [('partner_id', '=', r.partner_id.id), ('credit', '>', 0), ('account_id', '=', discount_check)])
                    aml_d = self.env['account.move.line'].search(
                        [('partner_id', '=', r.partner_id.id), ('debit', '>', 0), ('account_id', '=', discount_check)])
                    credit, debit = 0, 0

                    if aml_c: credit = sum([(self.bank_id.bank_id.loan_percentage / 100) * rec.credit for rec in aml_c])
                    if aml_d: debit = sum([(self.bank_id.bank_id.loan_percentage / 100) * rec.debit for rec in aml_d])

                    used = credit - debit
                    total_amount += (self.bank_id.bank_id.loan_percentage / 100) * r.amount
                    used_with_amount = (used * -1) + total_amount
                    check_numbers += r.check_number + ","
                if max_available < used_with_amount:
                    exceed = True

                if exceed:
                    if len(self.payment_ids) > 1:
                        msg += "- Total amount for check Number's ({}) to partner ({}) is ({}) exceed the central percentage ({}) in bank ({})\n" \
                               "old debt({}) current checks Loan amount({})  \n".format(
                            check_numbers[:-1], p.name, used_with_amount, max_available, self.bank_id.bank_id.name
                            , (used * -1), used_with_amount - (used * -1))
                    else:
                        msg += "- Total amount for check Number ({}) to partner ({}) is ({}) exceed the central percentage ({}) in bank ({})\n" \
                               "old debt({}) current checks Loan amount({})  \n".format(
                            check_numbers[:-1], p.name, used_with_amount, max_available, self.bank_id.bank_id.name
                            , (used * -1), used_with_amount - (used * -1))
            if len(msg) > 2:
                return msg

    def available_pool_validation_message(self, line):
        loan_account = self.bank_id.loan_account.id
        discount_check = self.bank_id.discount_check_account.id

        msg = ""
        #
        # aml_c = self.env['account.move.line'].search(
        #     [ ('credit', '>', 0), ('account_id', '=', discount_check)])
        # aml_d = self.env['account.move.line'].search(
        #     [ ('debit', '>', 0), ('account_id', '=', discount_check)])
        # credit, debit = 0, 0
        # if aml_c: credit = sum([(self.bank_id.bank_id.loan_percentage / 100) * rec.credit  for rec in aml_c ])
        # if aml_d: debit = sum([(self.bank_id.bank_id.loan_percentage / 100) * rec.debit for rec in aml_d ])
        # used = credit - debit
        used = 0
        available_pool = self.bank_id.bank_id.available_pool
        used_with_amount = 0
        check_numbers = ""
        total_amount = 0
        if line:
            total_amount += ((self.bank_id.bank_id.loan_percentage / 100) * line.amount)
            used_with_amount = (used * -1) + total_amount
            if available_pool < used_with_amount:
                msg += "- amount for check Number ({}) is exceed the available pool in bank ({}) \n".format(
                    line.check_number, self.bank_id.bank_id.name)
            if len(msg) > 2:

                return msg
            else:
                False
        else:
            total_amount = 0

            exceed = False
            for r in self.payment_ids:
                total_amount += ((self.bank_id.bank_id.loan_percentage / 100) * r.amount)
                used_with_amount = (used * -1) + total_amount
                check_numbers += r.check_number + ","
                if available_pool < used_with_amount:
                    exceed = True

            if exceed:
                msg = "- Total amount for this bank({}) is exceed the available pool  \n" \
                      "1-total debt({})  \n2-Total check Loan amount({})\n3-avaliable pool ({})".format(
                    self.bank_id.bank_id.name, (used * -1), used_with_amount - (used * -1), available_pool)

            if len(msg) > 6:
                return msg

    def time_min_limit(self):
        for rec in self:
            min_days = rec.bank_id.bank_id.min_num_of_days
            msg = ""

            from datetime import datetime
            for r in rec.payment_ids:
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>R ACTU",r.actual_date)
                actual_date = datetime.strptime(str(r.actual_date), '%Y-%m-%d').date()
                dif = actual_date - fields.date.today()

                if dif.days < min_days:
                    if dif.days > 1:
                        msg += "- you can collect this check ({}) from bank ({}) after {} days this duration is smaller than the minmum limit that define for this bank ({}) \n".format(
                            r.check_number, r.bank_name, dif.days, rec.bank_id.bank_id.name)
                    else:
                        msg += "- you can collect this check ({}) from bank ({}) after {} day this duration is smaller than the minmum limit that define for this bank ({}) \n".format(
                            r.check_number, r.bank_name, dif.days, rec.bank_id.bank_id.name)

            if len(msg) > 2:
                return msg

    def time_max_limit(self):
        for rec in self:

            max_days = rec.bank_id.bank_id.max_num_of_days
            msg = ""

            from datetime import datetime
            for r in rec.payment_ids:
                actual_date = datetime.strptime(str(r.actual_date), '%Y-%m-%d').date()
                dif = actual_date - fields.date.today()

                if dif.days > max_days:
                    msg += " you can collect this check  ({}) from bank ({}) after {} days this duration is greater than the maxmum limit that define for this bank ({}) \n".format(
                        r.check_number, r.bank_name, dif.days, rec.bank_id.bank_id.name)
            if len(msg) > 2:
                return msg


                # discount check part end
