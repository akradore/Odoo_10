# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JobCosting(models.Model):
    _inherit = 'job.costing'
    
    cost_estimate_ids = fields.Many2many(
        'sale.estimate.job',
        string='Estimations',
        stored=True,
        copy=False,
    )
    
    def action_view_job_estimate(self):
        action = self.env.ref('job_cost_estimate_customer.action_estimate_job').read()[0]
        action['domain'] = [('id', 'in', self.cost_estimate_ids.ids)]
        return action
