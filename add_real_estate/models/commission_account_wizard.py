# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class excelreportinehrit(models.TransientModel):
    _name = 'report.excel'

    excel_file = fields.Binary('Dowload report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)


class accountInvoiceLinewizard(models.TransientModel):
    _name = 'commission.account.wizard'

    excel_file = fields.Binary('Dowload report Excel', attachment=True, readonly=True)
    file_name = fields.Char('Excel File', size=64)
    commission_types_id = fields.Many2one(comodel_name="sale.commission", required=True,string="commission types",  )
    date_from = fields.Date(string='Start Date',required=True)
    date_to = fields.Date(string='End Date',required=True)

    def action_account_invoice_tax_search(self):

        data = []
        uid = self.env.user.id
        total_commission = 0
        if self.commission_types_id.contract_state == 'open':
            for broker in self.commission_types_id.salesmen2:
                account_move = self.env['account.move'].search(
                    [('state', '=', 'posted'),('broker_id','=',broker.id), ('invoice_date', '>',self.date_from),('invoice_date', '<', self.date_to)])

                total = 0
                for move in account_move:
                    total += move.amount_total
                commission = 0
                if self.commission_types_id.commission_type =="fixed":
                    commission = total * (self.commission_types_id.fix_qty/100)
                else:
                    for section in  self.commission_types_id.sections:
                        print("section.amount_from",section.amount_from)
                        print("section.amount_to",section.amount_to)
                        print("section.amount_from",total)
                        if section.amount_from <= total :
                            print("here 1")
                            if section.amount_to >= total:
                                print("here 2")
                                commission = total * (section.percent / 100)
                print("account_move :: ",account_move)
                print("account_move :: ",len(account_move))
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":"base"
                }))
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":""
                }))
                total_commission += commission
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":"Lines"
                }))
                if account_move:
                    for rec in account_move:
                            data.append(({
                                "name": rec.name,
                                "amount": rec.amount_total,
                                "header": ""
                            }))
                data.append(({
                    "name": '',
                    "amount": total,
                    "header": "total"
                }))
        elif self.commission_types_id.contract_state == 'paid':
            for broker in self.commission_types_id.salesmen2:
                account_payment = self.env['account.payment'].search(
                    [('state', '=', 'collected'),('broker_id','=',broker.id), ('payment_date', '>', self.date_from), ('payment_date', '<', self.date_to)])
                total = 0
                for move in account_payment:
                    total += move.amount
                commission = 0
                if self.commission_types_id.commission_type =="fixed":
                    commission = total * (self.commission_types_id.fix_qty/100)
                else:
                    for section in  self.commission_types_id.sections:
                        print("section.amount_from",section.amount_from)
                        print("section.amount_to",section.amount_to)
                        print("section.amount_from",total)
                        if section.amount_from <= total :
                            print("here 1")
                            if section.amount_to >= total:
                                print("here 2")
                                commission = total * (section.percent / 100)
                print("account_move :: ", account_payment)
                print("account_move :: ", len(account_payment))
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":"base"
                }))
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":""
                }))
                data.append(({
                    "name": broker.name,
                    "amount": commission,
                    "header":"Lines"
                }))
                if account_payment:
                    for rec in account_payment:
                            data.append(({
                                "name": rec.name,
                                "amount": rec.amount,
                                "header": ""
                            }))

                data.append(({
                    "name": '',
                    "amount": total,
                    "header": "total"
                }))
        if len(data) > 0 :
            act = self.generate_excel(data,total_commission)
            return {

                'type': 'ir.actions.act_window',
                'res_model': 'report.excel',
                'res_id': act.id,
                'view_type': 'form',
                'view_mode': 'form',
                'context': self.env.context,
                'target': 'new',
            }

        else:

            raise UserError(_('No Invoices for This '))


    def generate_excel(self, invoices_lines,total_commission):

        filename = 'commission Account '

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Account Invoices Report')

        without_borders = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'font_size': '11',

        })

        font_size_10_center = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})

        font_size_14_center = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 14, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})
        font_size_10 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 10, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})

        font_size_14 = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 14, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})
        font_size_total = workbook.add_format(
            {'font_name': 'KacstBook', 'font_size': 14, 'align': 'right', 'valign': 'vcenter', 'text_wrap': True,
             'border': 1})
        table_header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        table_header_formate_line = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#ebebe0',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        # header
        sheet.set_column(0, 0, 10, without_borders)
        sheet.set_column(1, 11, 20, without_borders)
        # sheet.write('A1', 'M', table_header_formate)


        row = 1
        row_test = 1
        col = 0
        c = 0
        d = 0
        print("invoices_lines : ",invoices_lines)
        for lines in invoices_lines:

            #     sheet.write(row, col, str(row_test) or '', font_size_10)
            print("lines['header']",lines['header'])
            if lines['header'] == "base":
                sheet.write(row, col + 0, 'Broker Name', table_header_formate)
                sheet.write(row, col + 1, 'Commission', table_header_formate)
            if lines['header'] == "":
                sheet.write(row, col + 0, lines['name'] or '', font_size_10)
                sheet.write(row, col + 1, lines['amount'] or '', font_size_10)
            if lines['header'] == "total":
                sheet.write(row, col + 0, "Total", font_size_14)
                sheet.write(row, col + 1, lines['amount'] or '', font_size_14)
            if lines['header'] == "Lines":
                sheet.write(row, col + 0, 'Name', table_header_formate_line)
                sheet.write(row, col + 1, 'Amount', table_header_formate_line)

            if lines['amount'] != '':
                row_test += 1
            row += 1
        sheet.write(row+2, col + 0, 'Total Commission', font_size_14)
        sheet.write(row+2, col + 1, total_commission, font_size_14)

        workbook.close()
        output.seek(0)

        self.write({'file_name': filename + str(datetime.today().strftime('%Y-%m-%d')) + '.xlsx'})
        self.excel_file = base64.b64encode(output.read())

        context = {
            'file_name': self.file_name,
            'excel_file': self.excel_file,
        }

        act_id = self.env['report.excel'].create(context)
        return act_id
