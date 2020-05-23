# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.addons.website_sale.controllers import main
from odoo.http import request


class PayfastController(http.Controller):
    return_url = '/payfast/return'
    cancel_url = '/payfast/cancel'
    notify_url = '/payfast/notify'

    @http.route('/payfast/return', type='http', auth='public', methods=['GET'], website=True, csrf=False)
    def payfast_after_payment(self, **post):
        if not request.session.get('sale_transaction_id'):
            return request.redirect('/shop/payment')
        transaction_id = request.session.get('sale_transaction_id')
        transaction = request.env['payment.transaction'].sudo().search([('id', '=', transaction_id)])
        post['reference'] = transaction.reference
        post['txn_id'] = transaction.id
        post['status'] = 'success'
        request.env['payment.transaction'].sudo().form_feedback(post, 'payfast')
        return request.redirect('/shop/confirmation')

    @http.route('/payfast/cancel', type='http', auth='public', methods=['GET'], website=True, csrf=False)
    def payfast_cancel_url(self, **post):
        request.session.update({'payfast_payment_cancel': True})
        return request.redirect('/shop/payment')


class payfastShop(main.WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth='public', website=True)
    def payment(self, **post):
        if 'payfast_payment_cancel' in request.session.keys():
            SaleOrder = request.env['sale.order']
            order = request.website.sale_get_order()
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection

            shipping_partner_id = False
            if order:
                if order.partner_shipping_id.id:
                    shipping_partner_id = order.partner_shipping_id.id
                else:
                    shipping_partner_id = order.partner_invoice_id.id

            values = {
                'website_sale_order': order
            }
            values['errors'] = SaleOrder._get_errors(order)
            values.update(SaleOrder._get_website_data(order))
            if not values['errors']:
                acquirers = request.env['payment.acquirer'].search(
                    [('website_published', '=', True), ('company_id', '=', order.company_id.id)]
                )
                values['acquirers'] = []
                for acquirer in acquirers:
                    acquirer_button = acquirer.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                        '/',
                        order.amount_total,
                        order.pricelist_id.currency_id.id,
                        values={
                            'return_url': '/shop/payment/validate',
                            'partner_id': shipping_partner_id,
                            'billing_partner_id': order.partner_invoice_id.id,
                        }
                    )
                    acquirer.button = acquirer_button
                    values['acquirers'].append(acquirer)

                values['tokens'] = request.env['payment.token'].search([('partner_id', '=', order.partner_id.id), ('acquirer_id', 'in', acquirers.ids)])
                values['errors'] = [['Your payment has been cancelled', 'Please try again']]
                request.session.pop('payfast_payment_cancel')
            return request.render('website_sale.payment', values)
        else:
            return super(payfastShop, self).payment()
