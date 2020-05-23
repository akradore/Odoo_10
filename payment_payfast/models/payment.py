# -*- coding: utf-'8' "-*-"
import logging
import urlparse
from odoo import api, fields, models
from odoo.http import request
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_payfast.controllers.main import PayfastController

_logger = logging.getLogger(__name__)


class AcquirerPayfast(models.Model):
    _inherit = 'payment.acquirer'

    merchant_id = fields.Char('Merchant ID', required_if_provider='payfast')
    merchant_key = fields.Char('Merchant Key', required_if_provider='payfast')
    provider = fields.Selection(selection_add=[('payfast', 'Payfast')])

    @api.multi
    def payfast_form_generate_values(self, values):
        sale_order_id = request.session.get('sale_last_order_id')
        sale_order = self.env['sale.order'].search([('id', '=', sale_order_id)])
        item_name = sale_order.order_line[0].product_id.name
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        reference = values.get('reference'),
        reference = reference[0]
        payfast_tx_values = dict(values)
        payfast_tx_values.update({
            'merchant_id': self.merchant_id,
            'merchant_key': self.merchant_key,
            'amount': values.get('amount'),
            'item_name': item_name,
            'return_url': '%s' % urlparse.urljoin(base_url, PayfastController.return_url),
            'cancel_url': '%s' % urlparse.urljoin(base_url, PayfastController.cancel_url),
            'notify_url': '%s' % urlparse.urljoin(base_url, PayfastController.notify_url),
            'reference': reference,
        })
        return payfast_tx_values

    @api.multi
    def payfast_get_form_action_url(self):
        if self.environment == 'prod':
            return 'https://www.payfast.co.za/eng/process'
        else:
            return 'https://sandbox.payfast.co.za/eng/process'


class TxAltapay(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _payfast_form_get_tx_from_data(self, data):
        reference = data.get('reference')
        tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'Payfast: received data for reference %s' % (reference)
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        return tx_ids[0]

    @api.multi
    def _payfast_form_validate(self, data):
        if data['status'] == 'success':
            self.write({'state': 'done'})
            return True
        else:
            self.write({'state': 'error'})
            return False
