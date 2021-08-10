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

        channelIds = '';
        aux = ''

        for s in params['channel_ids']:
            channelIds = aux + s
            aux = ','

        queryChannel = '''
            select tok.token,
                   app.server_key
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
                             where partner_id  in (%(channelIds)s)
                           ) t 
                       ) t
                 where sequential_bychannelid = sequential
                   and partner_id <> %(self.env.user.id)s
                 ) partners,
                 hermes_token tok,
                 hermes_apps app
             where tok.partner_id = partners.partner_id
               and app.id = tok.app_id
        '''
        tokens = self.env.cr.execute(queryChannel).fetchall()

        for token in tokens:
            print('x')
            body = {
                "to": token['token'],
                "notification": {
                    "title": params[0]['subject'],
                    "body": params[0]['body']
                }
            }

            header = {
                "Authorization": "key=" + token['server_key'],
                "Content-Type": "application/json"
            }

            r = requests.post("https://fcm.googleapis.com/fcm/send", data=json.dumps(body), headers=header) # Passar para o modo odoo
            print('x')

        return
