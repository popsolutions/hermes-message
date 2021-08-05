# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HermesMonitor(models.Model):

    _name = 'hermes.monitor'
    _description = 'Hermes Monitor'

    partner_id = fields.Many2one('res.partner', 'Vendor')
    idLastMessage = fields.Many2one('mail.message')
    idLastNotify = fields.Many2one('mail.message')

    @api.model
    def _checkNotify(self):
        print('x')

# select msg.res_id, msg.body
#   from hermes_monitor hrm,
#        mail_message msg
#  where msg.res_id = hrm.partner_id
#    and msg.id > greatest(hrm."idLastMessage", hrm."idLastNotify")
#  order by hrm.partner_id, msg.id
