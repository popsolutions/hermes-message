# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytest
import responses
import odoo.tests.common as common

class Teste_hermes_monitor(common.TransactionCase):
    @responses.activate
    def test_x(self):
        print('x')
        self.env['hermes.monitor'].checkNotify(self)
        print('y')

