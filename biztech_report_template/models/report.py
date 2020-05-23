# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api,_
from odoo.addons.base.ir.ir_qweb.qweb import QWeb

class Report(models.Model):
    _inherit = 'report'
    
    @api.model
    def get_html(self, docids, report_name, data=None):
        #res = super(Report, self).get_html(docids, report_name, data=data)
        invoice_obj = self.pool['account.invoice']#self.pool.get('account.invoice')
        if 'template' in report_name:
            for invoice in invoice_obj.browse(docids):
                report = self._get_report_from_name(cr, uid, invoice.report_template_id and invoice.report_template_id.report_name or invoice.partner_id and invoice.partner_id.report_template_id and invoice.partner_id.report_template_id.report_name or invoice.company_id and invoice.company_id.report_template_id and invoice.company_id.report_template_id.report_name)
                report_obj = self.pool[report.model]
                docs = report_obj.browse(docids)
                docargs = {
                    'doc_ids': ids,
                    'doc_model': report.model,
                    'docs': docs,
                }
                return self.render([], report.report_name, docargs)
        return super(Report, self).get_html(docids, report_name, data=data)

