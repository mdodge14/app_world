# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Answer(models.Model):
    _name = "answer"
    _description = "Answer"
    # _order = "name"

    name = fields.Char(index=True)
