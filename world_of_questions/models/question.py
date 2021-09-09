# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class Question(models.Model):
    _name = "question"
    _description = "Question"
    _order = "name"

    name = fields.Char(index=True, string='Question')
    solution_answers = fields.One2many('answer', 'question_id')
    correlated_yes_yes_questions = fields.Many2many('question', 'correlated_yes_yes_questions', 'if_id', 'then_id')
    correlated_yes_no_questions = fields.Many2many('question', 'correlated_yes_no_questions', 'if_id', 'then_id')
    correlated_no_no_questions = fields.Many2many('question', 'correlated_no_no_questions', 'if_id', 'then_id')
    correlated_no_yes_questions = fields.Many2many('question', 'correlated_no_yes_questions', 'if_id', 'then_id')
    debug = fields.Text()

    def run_correlations(self):
        answers = self.env['answer'].search([('question_id', '=', self.id)])
        self.debug = "Correlations added last:\n"
        for question_answer in answers:
            if question_answer.answer == 'yes':
                if self.correlated_yes_yes_questions:
                    for question in self.correlated_yes_yes_questions:
                        answer = self.env['answer'].search([('solution_id', '=', question_answer.solution_id.id), ('question_id', '=', question.id)], limit=1)
                        if not answer.id:
                            self.env['answer'].create({'solution_id': question_answer.solution_id.id, 'question_id': question.id, 'answer': 'yes'})
                            self.debug += "{} - {}? {}\n".format(question_answer.solution_id.name, question.name, 'yes')
                if self.correlated_yes_no_questions:
                    for question in self.correlated_yes_no_questions:
                        answer = self.env['answer'].search([('solution_id', '=', question_answer.solution_id.id), ('question_id', '=', question.id)], limit=1)
                        if not answer.id:
                            self.env['answer'].create({'solution_id': question_answer.solution_id.id, 'question_id': question.id, 'answer': 'no'})
                            self.debug += "{} - {}? {}\n".format(question_answer.solution_id.name, question.name, 'no')
            elif question_answer.answer == 'no':
                if self.correlated_no_no_questions:
                    for question in self.correlated_no_no_questions:
                        answer = self.env['answer'].search([('solution_id', '=', question_answer.solution_id.id), ('question_id', '=', question.id)], limit=1)
                        if not answer.id:
                            self.env['answer'].create({'solution_id': question_answer.solution_id.id, 'question_id': question.id, 'answer': 'no'})
                            self.debug += "{} - {}? {}\n".format(question_answer.solution_id.name, question.name, 'no')
                if self.correlated_no_yes_questions:
                    for question in self.correlated_no_yes_questions:
                        answer = self.env['answer'].search([('solution_id', '=', question_answer.solution_id.id), ('question_id', '=', question.id)], limit=1)
                        if not answer.id:
                            self.env['answer'].create({'solution_id': question_answer.solution_id.id, 'question_id': question.id, 'answer': 'yes'})
                            self.debug += "{} - {}? {}\n".format(question_answer.solution_id.name, question.name, 'yes')

    def add_answer(self):
        context = dict(
            self.env.context,
            default_question_id=self.id,
            default_for_solution=False
        )
        return {
            "name": "Add Answer",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "add.solution.answer.wizard",
            "target": "new",
            "binding_view_types": "form",
            "context": context,
        }
