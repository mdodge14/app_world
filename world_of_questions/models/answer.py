# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Answer(models.Model):
    _name = "answer"
    _description = "Answer"
    # _order = "name"

    solution_id = fields.Many2one('solution', string='Solution')
    question_id = fields.Many2one('question', string='Question')
    answer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Yes/No')
