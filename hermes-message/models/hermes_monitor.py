# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
import json

class HermesMonitor(models.Model):

    _name = 'hermes.monitor'
    _description = 'Hermes Monitor'

    partner_id = fields.Many2one('res.partner', 'Vendor')
    channel_id = fields.Many2one('mail.channel', 'Channel')
    idlastmessage = fields.Integer()
    idlastnotify = fields.Integer()

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        value = values[0]
        hermes_monitor = self.env['hermes.monitor'].search([('partner_id', '=', value['partner_id']), ('channel_id', '=', int(value['channel_id']))]);

        if hermes_monitor:
            lastMessage = {}

            if 'idlastmessage' in value:
                if value['idlastmessage'] > hermes_monitor.idlastmessage:
                    lastMessage.update({'idlastmessage': value['idlastmessage']})

            if 'idlastnotify' in value:
                if value['idlastnotify'] > hermes_monitor.idlastnotify:
                    lastMessage.update({'idlastnotify': value['idlastnotify']})

            if (lastMessage != {}):
                hermes_monitor.write(lastMessage)

            return hermes_monitor
        else:
            return super(HermesMonitor, self).create(value)

    @api.model
    def _checkNotify(self):
        # get messages that were not received or notified by the mobile device
        query = """
            select mm.id, mm.res_id, mm.body, mm.author_id
              from hermes_token ht,
                   mail_channel_partner mcp left join hermes_monitor hm 
                                                   on (hm.partner_id = mcp.partner_id and hm.channel_id = mcp.channel_id),
                   mail_message mm 
             where mcp.partner_id = ht.partner_id
               and mm.id > ht.idlastmessage /*consider from the moment the token loaded*/
               and mm.res_id = mcp.channel_id
               and mm.author_id <> mcp.partner_id /*disregard the author of the message*/
               and mm.id > greatest(coalesce(hm.idlastmessage, 0), coalesce(hm.idlastnotify, 0))
               and mm.message_type = 'comment'
            order by hm.partner_id, mm.id
        """

        self.env.cr.execute(query)
        messagesNotsend = self.env.cr.fetchall()

        for messageNotSend in messagesNotsend:
            # Sql to return users who participate in the message channel
            query = '''
                select partner_id
                  from mail_message_mail_channel_rel mmmcr,
                       mail_channel_partner mcp
                 where mmmcr.mail_message_id = ''' + str(messageNotSend[0]) + '''
                   and mcp.channel_id = mmmcr.mail_channel_id
            '''

            attachment_ids = []

            self.env.cr.execute(query)
            usersMessageChannel = self.env.cr.fetchall()

            for userMessageChannel in usersMessageChannel:
                attachment_ids.append(userMessageChannel[0]) #//t. provavemente não é mais necessário

            mail_message = {
                "parent_id": messageNotSend[0],
                "author_id": messageNotSend[3],
                "model": "mail.channel",
                "res_id": messageNotSend[1],
                "message_type": "mobilenotification",
                "subject": "Mensagem",
                "body": messageNotSend[2].replace('<p>', '').replace('</p>', ''),
                "channel_ids": [
                    messageNotSend[1]
                ]
            }

            self.env['mail.message'].create(mail_message)
        return
