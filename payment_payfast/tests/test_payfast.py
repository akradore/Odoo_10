# -*- coding: utf-8 -*-
from lxml import objectify
import odoo
import urlparse
from odoo.addons.payment_payfast.controllers.main import PayfastController
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import mute_logger


@odoo.tests.common.at_install(False)
@odoo.tests.common.post_install(True)
class PayfastCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(PayfastCommon, self).setUp()
        self.payfast = self.env.ref('payment.payment_acquirer_payfast')


class PayfastForm(PayfastCommon):

    def test_10_payfast_form_render(self):
        self.assertEqual(self.payfast.environment, 'test', 'test without test environment')
        self.payfast.write({'merchant_id': '10004091',
                            'merchant_key': 'ajlh6tyixqy19',
                            })
        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------

        # render the button
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        form_values = {'merchant_id': '10004091',
                       'merchant_key': 'ajlh6tyixqy19',
                       'amount': '1',
                       'return_url': '%s' % urlparse.urljoin(base_url, PayfastController.return_url),
                       'cancel_url': '%s' % urlparse.urljoin(base_url, PayfastController.cancel_url),
                       'notify_url': '%s' % urlparse.urljoin(base_url, PayfastController.notify_url),
                       'reference': 'SO100',
                       }
        # check form result
        res = self.payfast.render('test_ref0', 0.01, self.currency_euro.id, values=form_values, partner_id=None)
        tree = objectify.fromstring(res)
        self.assertEqual(tree.get('action'), 'https://sandbox.payfast.co.za/eng/process', 'payfast: wrong form POST url')
        for form_input in tree.input:
            if form_input.get('name') in ['currency', 'csrf_token', 'item_name']:
                continue
            self.assertEqual(form_input.get('value'), form_values[form_input.get('name')], 'payfast: wrong value for input %s: received %s instead of %s' % (form_input.get('name'), form_input.get('value'), form_values[form_input.get('name')]))

    @mute_logger('odoo.addons.payment_payfast.models.payment', 'ValidationError')
    def test_20_payfast_form_management(self):
        self.assertEqual(self.payfast.environment, 'test', 'test without test environment')

        # typical data posted by payfast after client has successfully paid
        payfast_post_data = {
            u'amount': u'1',
            u'reference': u'SO100',
            u'status': u'success',
        }

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(payfast_post_data, 'payfast')

        # create tx
        tx = self.env['payment.transaction'].create({
            'amount': 1,
            'acquirer_id': self.payfast.id,
            'currency_id': self.currency_euro.id,
            'reference': 'SO100',
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_france.id
        })

        # validate it
        tx.form_feedback(payfast_post_data, 'payfast')
        # check
        self.assertEqual(tx.state, 'done', 'payfast: wrong state after receiving a valid pending notification')
        # update tx
        tx.write({'state': 'draft', 'acquirer_reference': False})
        tx.form_feedback(payfast_post_data, 'payfast')
