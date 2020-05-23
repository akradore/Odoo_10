# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from openerp import fields, models, api, _
from datetime import date, time, datetime

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    invoice_credit_payment = fields.Selection([('full_amount', 'Full Amount(without credit)'), ('partial_amount', 'Partial Amount(with credit)')],string='',default='full_amount')
   

class res_partner(models.Model):
    _inherit = 'res.partner'

    custom_credit = fields.Float('Credit')

    @api.multi
    def action_view_credit_detail(self):
        self.ensure_one()

        partner_credit_ids = self.env['partner.credit'].search([('partner_id','=',self.id)])
        for payment_id in partner_credit_ids:
            self.env['partner.credit'].browse(payment_id)
            payment_id.do_update() 
        
        return {
            'name': 'Credit Details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            
            'res_model': 'partner.credit',
            'domain': [('partner_id', '=', self.id)],
            
        }

class partner_credit(models.Model):
    _name = 'partner.credit'

    partner_id = fields.Many2one('res.partner',"Customer")
    credit = fields.Float('Credit', readonly=True)
    update = fields.Float('Update')

    @api.multi
    def do_update(self):
        
        update_credit_history_obj = self.env['update.credit.history']
        
        
        if self.update > 0.00:
            self.credit = self.update
            val = {
                'date_update': datetime.now(),
		        'update_credit_amount' : self.update,
		        'old_credit_bal': self.partner_id.custom_credit,
		        'balance': self.partner_id.custom_credit + self.update,
		        'partner_id': self.partner_id.id,
            }
            update_credit_history_obj.create(val)
            self.partner_id.custom_credit = self.partner_id.custom_credit + self.credit
        
        if self.partner_id.custom_credit != 0.00:
            
            self.credit = self.partner_id.custom_credit
        self.update = 0.00                
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            update = self.partner_id.update 
            return {'credit':update}

class UpdateCreditHistory(models.Model):
    _name = 'update.credit.history'
    
    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')

class UpdateCreditHistoryPayment(models.Model):
    _name = 'update.credit.history.payment'
    
    date_update = fields.Date('Date')
    update_credit_amount = fields.Float('Update Credit amount')
    old_credit_bal = fields.Float('Old Credit Balance')
    payment_refer = fields.Many2one('account.payment', 'Payment Ref.')
    balance = fields.Float('Balance')
    partner_id = fields.Many2one('res.partner', 'Customer')

class UpdateCreditAccount(models.TransientModel):
    _name = 'credit.account'
    
    credit_amount = fields.Float('Credit Amount',required="True")
    journal_id = fields.Many2one('account.journal', 'Payment Journal',required="True")
    credit_id = fields.Many2one('partner.credit', 'Customer')
    #partner_id = fields.Many2one('res.partner', 'Customer', related='credit_id.partner_id')
    
    @api.multi
    def post(self):
        context = self._context
        active_ids = context.get('active_ids')
        account_payment_obj = self.env['account.payment']
        partner_credit_id = self.env['partner.credit'].browse(active_ids[0])
        update_credit_payment_history_obj = self.env['update.credit.history.payment']
        
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')
        
        vals = {}
        
        vals = {
            'name' : self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code('account.payment.customer.invoice'),
            'payment_type' : "inbound",
            'amount' : self.credit_amount,
            #'move' : account_payment_obj._create_payment_entry(amount),
            'communication' : "Credit Recharge",
            'payment_date' : datetime.now().date(),
            'journal_id' : self.journal_id.id,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': partner_credit_id.partner_id.id,
        }
        
        payment_create = account_payment_obj.create(vals)
        if partner_credit_id.credit >= 0.00:
            partner_credit_id.credit = payment_create.amount
            value = {
                'date_update': datetime.now(),
		        'update_credit_amount' : partner_credit_id.credit,
		        'old_credit_bal': partner_credit_id.partner_id.custom_credit,
		        'balance': partner_credit_id.partner_id.custom_credit + partner_credit_id.credit,
		        'partner_id': partner_credit_id.partner_id.id,
		        'payment_refer' : payment_create.id,
            }
            update_credit_payment_history_obj.create(value)
            partner_credit_id.partner_id.custom_credit = partner_credit_id.partner_id.custom_credit + partner_credit_id.credit
        
        if partner_credit_id.partner_id.custom_credit != 0.00:
            partner_credit_id.credit = partner_credit_id.partner_id.custom_credit
            
        return
        


class account_journal(models.Model):
    _inherit = 'account.journal'

    credit = fields.Boolean(string='POS Credit Journal')        
    
    
class pos_order(models.Model):
    _inherit = 'pos.order'
    
    credit_check = fields.Boolean('Credit')
    
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a pos order.
        """
        return {
            'name': self.name,
            'origin': self.name,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'company_id': self.company_id.id,
            'type': 'out_invoice',
            'reference': self.name,
            'partner_id': self.partner_id.id,
            'comment': self.note or '',
            # considering partner's sale pricelist's currency
            'currency_id': self.pricelist_id.currency_id.id,
            'user_id': self.env.uid,
        }
    
    
    def _action_create_invoice_line_cr(self, line=False, invoice_id=False):
        InvoiceLine = self.env['account.invoice.line']
        inv_name = line.product_id.name_get()[0][1]
        inv_line = {
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty,
            'account_analytic_id': self._prepare_analytic_account(line),
            'name': inv_name,
        }
        
        # Oldlin trick
        invoice_line = InvoiceLine.sudo().new(inv_line)
        invoice_line._onchange_product_id()
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id).ids
        fiscal_position_id = line.order_id.fiscal_position_id
        if fiscal_position_id:
            invoice_line.invoice_line_tax_ids = fiscal_position_id.map_tax(invoice_line.invoice_line_tax_ids, line.product_id, line.order_id.partner_id)
        invoice_line.invoice_line_tax_ids = invoice_line.invoice_line_tax_ids.ids
        # We convert a new id object back to a dictionary to write to
        # bridge between old and new api
        inv_line = invoice_line._convert_to_write({name: invoice_line[name] for name in invoice_line._cache})
        inv_line.update(price_unit=line.price_unit, discount=line.discount, name=inv_name)
        #InvoiceLine.sudo().create(inv_line1)
        return InvoiceLine.sudo().create(inv_line)
    
    
    @api.multi
    def action_pos_order_credit_invoice(self, cr_journal):
        Invoice = self.env['account.invoice']

        for order in self:
            # Force company for all SUPERUSER_ID action
            local_context = dict(self.env.context, force_company=order.company_id.id, company_id=order.company_id.id)
            if order.invoice_id:
                Invoice += order.invoice_id
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            invoice = Invoice.new(order._prepare_invoice())
            invoice._onchange_partner_id()
            invoice.fiscal_position_id = order.fiscal_position_id

            inv = invoice._convert_to_write({name: invoice[name] for name in invoice._cache})
            new_invoice = Invoice.with_context(local_context).sudo().create(inv)
            message = _("This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (order.id, order.name)
            new_invoice.message_post(body=message)
            order.write({'invoice_id': new_invoice.id, 'state': 'invoiced'})
            Invoice += new_invoice

            for line in order.lines:
                self.with_context(local_context)._action_create_invoice_line_cr(line, new_invoice.id)

            account_obj = self.env['account.account'].search([('internal_type','=', 'other')], limit=1)
            
            inv_line1 = {
                'invoice_id': new_invoice.id,
                'quantity': 1,
                #'account_analytic_id': self._prepare_analytic_account(line),
                'name': 'Credit',
                'price_unit': - float(cr_journal),
                'account_id': account_obj.id, 
                
            }
            
            line_obj = self.env['account.invoice.line']
            line_obj.create(inv_line1)
            
            new_invoice.with_context(local_context).sudo().compute_taxes()
            order.sudo().write({'state': 'invoiced'})

        if not Invoice:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('account.invoice_form').id,
            'res_model': 'account.invoice',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': Invoice and Invoice.ids[0] or False,
        }

    
    @api.model
    def create_from_ui(self, orders):
        # Keep only new orders
        submitted_references = [o['data']['name'] for o in orders]
        pos_order = self.search([('pos_reference', 'in', submitted_references)])
        existing_orders = pos_order.read(['pos_reference'])
        existing_references = set([o['pos_reference'] for o in existing_orders])
        orders_to_save = [o for o in orders if o['data']['name'] not in existing_references]
        order_ids = []
        history_line_obj = self.env['credit.history']

        for tmp_order in orders_to_save:
            to_invoice = tmp_order['to_invoice']
            order = tmp_order['data']
            
            print "tttttttttttttttttttttttttttttttttttttttttttttt",order, self

            add_credit_in_invoice = False

            if to_invoice:
                self._match_payment_to_invoice(order)
            pos_order = self._process_order(order)
            order_ids.append(pos_order.id)
            
            print 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',pos_order
            
            pos_order_id = self.browse(pos_order.id)
            for pos_credit in pos_order_id.statement_ids:
                if pos_credit.journal_id.credit == True:
                    vals = {
                        'pos_order_id': pos_order.id,
                        'partner_id': pos_order_id.partner_id.id,
                        'used_credit_amount' :pos_credit.amount,
                        'date' : pos_order_id.date_order,
                        'pos_order_amount' : pos_order_id.amount_total,
                        'balance_credit_amount' : pos_order_id.partner_id.custom_credit,
                    }
                    history_line_obj.sudo().create(vals)

            print "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.OperationalError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

            if to_invoice:
                journal_custom_id = self.env['account.journal']
                cr_journal = 0.0
                for st in orders:
                    ps = self.env['pos.session'].search([('id','=',st['data']['pos_session_id'])])
                    add_credit_in_invoice = ps.config_id.invoice_credit_payment
                    for st1 in st['data']['statement_ids']:
                       credit_jour = journal_custom_id.search([('id','=', st1[2]['journal_id']),('credit','=', True)])
                       if credit_jour:
                           cr_journal = (st1[2]['amount'])
                
                # if cr_journal:
                #     pos_order.action_pos_order_credit_invoice(cr_journal)
                #     pos_order.invoice_id.sudo().action_invoice_open()
                #     pos_order.account_move = pos_order.invoice_id.move_id
                # else:
                #     pos_order.action_pos_order_invoice()
                #     pos_order.invoice_id.sudo().action_invoice_open()
                #     pos_order.account_move = pos_order.invoice_id.move_id



                if cr_journal and add_credit_in_invoice == 'full_amount':
                    pos_order.action_pos_order_invoice()
                    pos_order.invoice_id.sudo().action_invoice_open()
                    pos_order.account_move = pos_order.invoice_id.move_id

                elif cr_journal and add_credit_in_invoice == 'partial_amount':
                    pos_order.action_pos_order_credit_invoice(cr_journal)
                    pos_order.invoice_id.sudo().action_invoice_open()
                    pos_order.account_move = pos_order.invoice_id.move_id

                else:
                    pos_order.action_pos_order_invoice()
                    pos_order.invoice_id.sudo().action_invoice_open()
                    pos_order.account_move = pos_order.invoice_id.move_id

        print "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo", order_ids
        return order_ids
    
    
    
    '''@api.model
    def create_from_ui(self, orders):
        
        history_line_obj = self.env['credit.history']
        
        order_ids = super(pos_order, self).create_from_ui(orders)
        
        for order_id in order_ids:
            pos_order_id = self.browse(order_id)
            for pos_credit in pos_order_id.statement_ids:
                if pos_credit.journal_id.credit == True:
                    vals = {
                        'pos_order_id': order_id,
                        'partner_id': pos_order_id.partner_id.id,
                        'used_credit_amount' :pos_credit.amount,
                        'date' : pos_order_id.date_order,
                        'pos_order_amount' : pos_order_id.amount_total,
                        'balance_credit_amount' : pos_order_id.partner_id.custom_credit,
                    }
                    history_line_obj.sudo().create(vals)		
                
        return order_ids'''

