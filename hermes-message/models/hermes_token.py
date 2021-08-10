# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import api, fields, models, _
from datetime import datetime, timedelta


class HermesToken(models.Model):

    _name = 'hermes.token'
    _description = 'Hermes Token'  # TODO

    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    app_id = fields.Many2one('hermes.apps')
    token = fields.Char()
    startsession = fields.Datetime()
    endsession = fields.Datetime()
    lastbeep = fields.Datetime()

    @api.model
    def create(self, vals):

        app = self.env['hermes.apps'].search(
                [['app_id', '=', vals['app_id']]]);

        if not app:
            raise Exception('App "' + vals['app_id'] + '" not Found')

        tokens = self.env['hermes.token'].search(
                [['partner_id', '=', int(vals['partner_id'])]]);

        vals['app_id'] = app['id'];
        vals['startsession'] = datetime.now();
        vals['startsession'] = datetime.now();
        vals['endsession'] = None;

        if tokens:
            for token in tokens:
                token.write(
                   vals
                )
            return tokens
        else:
            return super(HermesToken, self).create(vals)
