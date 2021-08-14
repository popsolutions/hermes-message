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
            self.sendModileNotification(values, res.id)

        return res


    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        idLastMessage = 0

        for arg in args:
            if ((arg[0] == 'id') and (arg[1] == '>')):
                idLastMessage = int(arg[2]);

            if (arg[0] == 'res_id'):
                partner_id = arg[2];

        res = super(MailMessage, self)._search(
            args, offset=offset, limit=limit, order=order,
            count=count, access_rights_uid=access_rights_uid)

        if idLastMessage > 0:
            self.env['hermes.monitor'].create(
                    {'partner_id' : partner_id,
                    'idlastmessage' : idLastMessage}
                );

        return res

    def sendModileNotification(self, params, idlastnotify):

        channelIds = '';
        aux = ''

        for s in params[0]['channel_ids'][0]:
            channelIds = channelIds + aux + str(s)
            aux = ','

        queryChannel = '''
            select tok.token,
                   app.server_key,
                   partners.partner_id
              from (select partner_id
                      from (
                    select channel_id, 
                           partner_id, 
                           ROW_NUMBER() over(partition by channel_id order by channel_id desc) sequential_bychannelid,
                           ROW_NUMBER() over(order by channel_id desc) sequential
                      from (select channel_id, 
                                   partner_id, 
                                   lag(channel_id) over(order by channel_id) 
                              from mail_channel_partner mcp 
                             where partner_id  in (''' + channelIds + ''')
                           ) t 
                       ) t
                 where sequential_bychannelid = sequential
                   and partner_id <> ''' + str(self.env.user.id) + '''
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
                    "title": params[0]['subject'],
                    "body": params[0]['body']
                }
            }

            header = {
                "Authorization": "key=" + token[1],
                "Content-Type": "application/json"
            }

            r = requests.post("https://fcm.googleapis.com/fcm/send", data=json.dumps(body), headers=header) # Passar para o modo odoo

            self.env['hermes.monitor'].create(
                    {'partner_id' : token[2],
                    'idlastnotify' : idlastnotify}
                );

        return
