# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleEstimateJob(models.Model):
    _inherit = 'sale.estimate.job'
    
    jobcost_id = fields.Many2one(
        'job.costing',
        string='Jobcost Sheet',
    )
    
    def action_view_job_cost_sheet(self):
        action = self.env.ref('odoo_job_costing_management.action_job_costing').read()[0]
        action['domain'] = [('id', 'in', self.jobcost_id.ids)]
        return action
