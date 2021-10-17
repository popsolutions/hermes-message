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
        # values = {'author_id': 78, 'model': 'mail.channel', 'res_id': 78, 'message_type': 'mobilenotification', 'subject': 'Teste-postman', 'body': 'Mateus-Quinta', 'channel_ids': [[3, 78]]}

        res = super(MailMessage, self).create(values)
        print(values[0])

        if values[0]['message_type'] == 'mobilenotification':
            self.sendModileNotification(values, values[0]['parent_id'])

        return res

    def sendModileNotification(self, params, idlastnotify):
        # params example = {'author_id': 1, 'res_id': 78, 'subject': 'Título Mensagem', 'body': 'Mensagem']}

        for param in params:
            channelId = str(param['res_id'])
            parent_id = 0

            if 'parent_id' in param:
                parent_id = param['parent_id']

            queryChannel = '''
            /***Getting token and server key from contacts involved in the messagem channel***/
                select tok.token,
                       app.server_key,
                       partners.partner_id
                  from ( select mcp.partner_id 
                       from mail_channel_partner mcp 
                      where channel_id = ''' + channelId + ''' 
                        and partner_id <> ''' + str(param['author_id']) + '''
                     ) partners,
                     hermes_token tok,
                     hermes_apps app
                 where tok.partner_id = partners.partner_id
                   and app.id = tok.app_id
            '''

            self.env.cr.execute(queryChannel)
            tokens = self.env.cr.fetchall()

            for token in tokens:
                body = {
                    "to": token[0],
                    "notification": {
                        "title": param['subject'],
                        "body": param['body'],

                    },
                    "data":{
                        "channel_id": channelId,
                        "mail_message_id": parent_id
                    }
                }

                header = {
                    "Authorization": "key=" + token[1],
                    "Content-Type": "application/json"
                }

                r = requests.post("https://fcm.googleapis.com/fcm/send", data=json.dumps(body), headers=header) # Passar para o modo odoo

                if idlastnotify != 0:
                    self.env['hermes.monitor'].create(
                            {'partner_id': token[2],
                            'idlastnotify': idlastnotify,
                            'channel_id' : channelId
                             }
                        )

        return
