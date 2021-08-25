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


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        idLastMessage = 0

        for arg in args:
            if ((arg[0] == 'id') and (arg[1] == '>') and (str(arg[2]).isdigit())): #  sample: ["id", ">","400"]
                idLastMessage = int(arg[2]);

            if (arg[0] == 'res_id'):
                channel_id = arg[2];

        res = super(MailMessage, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)

        if idLastMessage > 0:
            self.env['hermes.monitor'].create(
                    {'partner_id': self.env.user.partner_id.id,
                     'idlastmessage': idLastMessage,
                     'channel_id': channel_id}
                );

        return res

    def sendModileNotification(self, params, idlastnotify):

        param = params[0];
        channelIds = '';
        aux = ''

        for s in param['channel_ids']:
            channelIds = channelIds + aux + str(s)
            aux = ','

        queryChannel = '''
        /***Getting token and server key from contacts involved in the messagem channel***/
            select tok.token,
                   app.server_key,
                   partners.partner_id
              from ( select mcp.partner_id 
                   from mail_channel_partner mcp 
                  where channel_id in (''' + channelIds + ''') 
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
                    "channel_id": channelIds,
                    "mail_message_id": param['parent_id']
                }
            }

            header = {
                "Authorization": "key=" + token[1],
                "Content-Type": "application/json"
            }

            r = requests.post("https://fcm.googleapis.com/fcm/send", data=json.dumps(body), headers=header) # Passar para o modo odoo

            self.env['hermes.monitor'].create(
                    {'partner_id' : token[2],
                    'idlastnotify' : idlastnotify,
                    'channel_id' : param['res_id']
                     }
                );

        return
