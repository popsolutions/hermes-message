# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import requests
import json

class MailMessage(models.Model):

    _inherit = 'mail.message'

    message_type = fields.Selection(selection_add=[('mobilenotification', 'Mobile Notification')])

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        res = super(MailMessage, self).create(values)
        print(values[0])

        if values[0]['message_type'] == 'mobilenotification':
            self.sendModileNotification(values)

        return res


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        idLastMessage = 0

        for arg in args:
            if ((arg[0] == 'id') and (arg[1] == '>')):
                idLastMessage = int(arg[2]);

            if (arg[0] == 'res_id'):
                partner_id = arg[2];

        if idLastMessage > 0:
            hermes_monitor = self.env['hermes.monitor'].search(
                [['partner_id', '=', partner_id]]);

            if hermes_monitor:
                hermes_monitor.write({'idLastMessage' : idLastMessage});
            else:
                hermes_monitor.create(
                    {'partner_id' : partner_id,
                    'idLastMessage' : idLastMessage}
                );

        return super(MailMessage, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)

    def sendModileNotification(self, params):

        print('x')
        body = {
            "to": "DUaErLmS9GR4ncTozKnMF:APA91bG-BAGE0-mYipRCpbXV20WVDhkQpnoGxScrYKR9-_kHXVB9pFle0q9eOpEGJJJhmA-INSTw-Xw_murnXHG6jxl0_UWr6FPDT4k_GTLMH6LO2b5SVAbslHCAERiLoWwi0T6v9gNpe",
            "notification": {
                "title": params[0]['subject'],
                "body": params[0]['body']
            }
        }

        header = {
            "Authorization": "key=AAAVatm1Mg:APA91bEeST6zN_G8ll5FlHSa75Qc5y6lL76w_ZzDdNXi_iS1HdrDVk83DROKj7AvlVrxE9KObQP6mwSjm2uETjGn8bFmfzOIQ9qGAEYI6pHlpW9WzKG-AsPuf_G6vKuPulgw365FMMSAA",
            "Content-Type": "application/json"
        }

        r = requests.post("https://fcm.googleapis.com/fcm/send", data=json.dumps(body), headers=header)
        print('x')
        return
