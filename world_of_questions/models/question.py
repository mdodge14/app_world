# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Question(models.Model):
    _name = "question"
    _description = "Question"
    _order = "sequence, name"

    name = fields.Char(index=True, string='Question')
    sequence = fields.Integer('Sequence', index=True)
    possible_solution = fields.Boolean()
