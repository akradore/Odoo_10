# -*- coding: utf-8 -*-
import pytz
from datetime import datetime, timedelta

import logging
from odoo import fields, SUPERUSER_ID
from odoo.http import request
from odoo import api, exceptions, fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def get_booking_date(self, times="0:0", date=None):
        booking_times = times.split(":")
        booking_time = int(booking_times[0]) * 60 + int(booking_times[1])
        return datetime.strptime(str(date), '%d/%m/%Y') + timedelta(minutes=booking_time)

    def get_utc_date(self, date=None, timezone=None):
        to_zone = pytz.timezone('UTC')
        from_zone = pytz.timezone(timezone)
        return from_zone.localize(date).astimezone(to_zone)


    @api.model
    def form_feedback(self, data, acquirer_name):
        tx = None
        res = super(PaymentTransaction, self).form_feedback(data, acquirer_name)
        try:
            tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
            if hasattr(self, tx_find_method_name):
                tx = getattr(self, tx_find_method_name)(data)
            _logger.info('<%s> transaction processed: tx ref:%s, tx amount: %s', acquirer_name, tx.reference if tx else 'n/a', tx.amount if tx else 'n/a')

            tx.write({'state': 'done'})
            if tx and tx.sale_order_id:
                # verify SO/TX match, excluding tx.fees which are currently not included in SO
                amount_matches = (tx.sale_order_id.state in ['draft', 'sent'] and float_compare(tx.amount, tx.sale_order_id.amount_total, 2) == 0)
                if amount_matches:
                    if tx.state == 'done' and tx.acquirer_id.auto_confirm == 'none':
                        _logger.info('<%s> transaction completed, auto-confirming order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)
                        print "before"
                        for line in tx.sale_order_id.order_line:
                            if line.appointment_id:
                                for app in line.appointment_id:
                                    name = '%s-%s' % (tx.sale_order_id.partner_id.name, app.click_time_dt)
                                    app.write({
                                        'name': name,
                                        'status': 'booked',
                                        'app_state': 'done',
                                        #'partner_ids': [(4, tx.sale_order_id.partner_id.id)]
                                        'partner_ids': [(4, [tx.sale_order_id.partner_id.id, app.app_partner_id.id])]
                                    })
                        tx.sale_order_id.sudo().with_context(send_email=True).action_confirm()
                    elif tx.state not in ['cancel', 'error'] and tx.sale_order_id.state == 'draft':
                        _logger.info('<%s> transaction pending/to confirm manually, sending quote email for order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)

                        tx.sale_order_id.sudo().force_quotation_send()
                else:
                    _logger.warning('<%s> transaction MISMATCH for order %s (ID %s)', acquirer_name, tx.sale_order_id.name, tx.sale_order_id.id)
        except Exception:
            _logger.exception('Fail to confirm the order or send the confirmation email%s', tx and ' for the transaction %s' % tx.reference or '')

        return res
