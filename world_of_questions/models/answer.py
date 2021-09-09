# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Answer(models.Model):
    _name = "answer"
    _description = "Answer"
    _order = "is_solution desc, answer desc, name"

    name = fields.Char(compute='compute_name')
    solution_id = fields.Many2one('solution', string='Solution')
    question_id = fields.Many2one('question', string='Question')
    answer = fields.Selection([('yes', 'Yes'), ('no', 'No'), ('sometimes', 'Sometimes'), ('kindof', 'Kind of')], string='Answer')
    is_solution = fields.Boolean()

    @api.depends('question_id', 'answer')
    def compute_name(self):
        for rec in self:
            rec.name = ""
            if rec.question_id.name and rec.answer:
                rec.name = "{}: {}? {}".format(rec.solution_id.name, rec.question_id.name, rec.answer)

    @api.model
    def create(self, vals):
        res = super(Answer, self).create(vals)
        if res.answer == 'yes' and res.solution_id.id and res.question_id.id:
            if res.question_id.correlated_yes_yes_questions:
                for question in res.question_id.correlated_yes_yes_questions:
                    answer = self.env['answer'].search([('solution_id', '=', res.solution_id.id), ('question_id', '=', question.id)], limit=1)
                    if not answer.id:
                        self.env['answer'].create({'solution_id': res.solution_id.id, 'question_id': question.id, 'answer': 'yes'})
            if res.question_id.correlated_yes_no_questions:
                for question in res.question_id.correlated_yes_no_questions:
                    answer = self.env['answer'].search([('solution_id', '=', res.solution_id.id), ('question_id', '=', question.id)], limit=1)
                    if not answer.id:
                        self.env['answer'].create({'solution_id': res.solution_id.id, 'question_id': question.id, 'answer': 'no'})
        elif res.answer == 'no' and res.solution_id.id and res.question_id.id:
            if res.question_id.correlated_no_no_questions:
                for question in res.question_id.correlated_no_no_questions:
                    answer = self.env['answer'].search([('solution_id', '=', res.solution_id.id), ('question_id', '=', question.id)], limit=1)
                    if not answer.id:
                        self.env['answer'].create({'solution_id': res.solution_id.id, 'question_id': question.id, 'answer': 'no'})
            if res.question_id.correlated_no_yes_questions:
                for question in res.question_id.correlated_no_yes_questions:
                    answer = self.env['answer'].search([('solution_id', '=', res.solution_id.id), ('question_id', '=', question.id)], limit=1)
                    if not answer.id:
                        self.env['answer'].create({'solution_id': res.solution_id.id, 'question_id': question.id, 'answer': 'yes'})
        return res
