# Copyright 2021 Pop Solutions
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class MailMessage(models.Model):

    _inherit = 'mail.message'

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

        print('x')
