# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hermes-message',
    'summary': """
        Hermes Message""",
    'version': '12.0.21.08',
    'license': 'AGPL-3',
    'author': 'Pop Solutions,Odoo Community Association (OCA)',
    'website': 'www.popsolutions.co',
    'depends': [
        'mail'
    ],
    'data': [
        'views/hermes_menu.xml',
        'security/hermes_token.xml',
        'views/hermes_token.xml',
        'security/hermes_apps.xml',
        'views/hermes_apps.xml',
        'security/hermes_monitor.xml',
        'views/hermes_monitor.xml',
    ],
    'demo': [
    ],
}
