# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import fields, models, api, tools

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def _default_report_template(self):
        report_obj = self.env['ir.actions.report.xml']
        report_id = report_obj.search([('model', '=', 'account.invoice'), ('report_name' ,'=', 'biztech_report_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'account.invoice')])[0]
        return report_id

    @api.one
    def _default_report_template1(self):
        report_obj = self.env['ir.actions.report.xml']
        report_id = report_obj.search([('model', '=', 'account.invoice'), ('report_name' ,'=', 'biztech_report_template.report_invoice_template_custom')])
        if report_id:
            report_id = report_id[0]
        else:
            report_id = report_obj.search([('model', '=', 'account.invoice')])[0]
        if self.report_template_id and self.report_template_id.id < report_id.id:
            self.write({'report_template_id': report_id and report_id.id or False})
            #self.report_template_id = report_id and report_id.id or False
        self.report_template_id1 = report_id and report_id.id or False

    report_template_id1 = fields.Many2one('ir.actions.report.xml' , string="Invoice Template", compute='_default_report_template1', help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
    report_template_id = fields.Many2one('ir.actions.report.xml' , string="Invoice Template", help="Please select Template report for Invoice", domain=[('model', '=', 'account.invoice')])
