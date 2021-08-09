# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HermesNotifyservers(models.Model):

    _name = 'hermes.notifyservers'
    _description = 'Hermes Notifyservers'

    name = fields.Char()
    description = fields.Char()
    key = fields.Char()
    server_name = fields.Selection(
        [
            ('firebase', 'firebase')
        ]
    )

    create_date = fields.Date(
        readonly=True,
    )
