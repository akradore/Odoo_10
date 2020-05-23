# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp import fields, models, api, _
from datetime import date, time, datetime


class res_partner(models.Model):
    _inherit = 'res.partner'

    custom_credit = fields.Float('Credit')

    @api.multi
    def action_view_credit_detail(self):
        self.ensure_one()

        partner_credit_ids = self.env['partner.credit'].search([('partner_id','=',self.id)])
        for payment_id in partner_credit_ids:
            print  "==============>",payment_id
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
        if self.update > 0.00:
            self.credit = self.update
            self.partner_id.custom_credit = self.credit
        if self.partner_id.custom_credit != 0.00:
            
            self.credit = self.partner_id.custom_credit
        self.update = 0.00                
    
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            update = self.partner_id.update 
            return {'credit':update}


class account_journal(models.Model):
    _inherit = 'account.journal'

    credit = fields.Boolean(string='POS Credit Journal')        
