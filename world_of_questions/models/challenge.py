# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)

class Challenge(models.Model):
    _name = "challenge"
    _description = "Challenge"
    # _order = "name"

    name = fields.Char(index=True)
    state = fields.Char(default="new")
    message = fields.Char(default="Hi there, would you like to play 20 questions?", readonly=True)
    asked_question_ids = fields.Many2many('question', 'challenge_asked_questions', 'cid', 'qid')

    def yes_action(self):
        if self.state in ('new', 'not playing'):
            self.name = "Great! I'll be the guesser. Do you know what you are?"
            self.state = 'ready'
        elif self.state in ('ready', 'ask'):
            self.ask_question()

    def no_action(self):
        if self.state in ('new', 'ready'):
            self.name = "OK, I'll be here when you're ready to play."
            self.state = 'not playing'
        elif self.state == 'ask':
            self.ask_question()

    def start_over(self):
        self.state = 'new'
        self.name = "Hi there, would you like to play 20 questions?"
        self.asked_question_ids = [(5, 0, 0)]

    def ask_question(self):
        if self.asked_question_ids:
            question = self.env['question'].search([('id', 'not in', self.asked_question_ids.ids)], order='sequence asc', limit=1)
        else:
            question = self.env['question'].search([], order='sequence asc', limit=1)
        self.asked_question_ids = [(4, question.id)]
        number = len(self.asked_question_ids) if self.asked_question_ids else 1
        self.name = "Got it. Here's question #{}: {}?".format(number, question.name)
        self.state = 'ask'
