{
    'name': 'Cheque Management',
    'author': 'Centione',
    'data': [
        'security/ir.model.access.csv',
        'wizard/warning_popUp.xml',
        'views/account_bank_journal_inherit.xml',
        'views/payment_view_inherit.xml',
        'views/account_account.xml',
        'views/payment_in_batch_deposit.xml',
        'views/res_bank_view_inherit.xml',
        'views/account_batch_deposit_inherit.xml',

    ],
    'depends': ['account','account_batch_payment', 'base', 'account_check_printing'],
    'category': 'Accounting & Banking',
    'installable': True,
    'auto_install': False,
    'application': True
}

