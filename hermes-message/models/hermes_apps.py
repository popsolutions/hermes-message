# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HermesApps(models.Model):

    _name = 'hermes.apps'
    _description = 'Hermes Apps'

    name = fields.Char()
    app_id = fields.Char('App Id')
    server_key = fields.Char()
    description = fields.Char()
    server_name = fields.Selection(
        [
            ('firebase', 'firebase')
        ]
    )

    create_date = fields.Date(
        readonly=True,
    )
