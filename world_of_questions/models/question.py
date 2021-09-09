# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Question(models.Model):
    _name = "question"
    _description = "Question"
    _order = "name"

    name = fields.Char(index=True, string='Question')
    correlated_yes_yes_questions = fields.Many2many('question', 'correlated_yes_yes_questions', 'if_id', 'then_id')
    correlated_yes_no_questions = fields.Many2many('question', 'correlated_yes_no_questions', 'if_id', 'then_id')
    correlated_no_no_questions = fields.Many2many('question', 'correlated_no_no_questions', 'if_id', 'then_id')
    correlated_no_yes_questions = fields.Many2many('question', 'correlated_no_yes_questions', 'if_id', 'then_id')
