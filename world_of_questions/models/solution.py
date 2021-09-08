# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Solution(models.Model):
    _name = "solution"
    _description = "Solution"
    # _order = "name"

    name = fields.Char(index=True)
    article = fields.Selection([('a', 'a'), ('an', 'an'), ('the', 'the')], default='a')
