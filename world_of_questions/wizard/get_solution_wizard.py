# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _


class GetSolutionWizard(models.TransientModel):
    _name = 'get.solution.wizard'
    _description = 'Get Solution Wizard'

    challenge_id = fields.Many2one('challenge', string='Challenge')
    solution = fields.Char()
    article = fields.Selection([('a', 'a'), ('an', 'an'), ('the', 'the')], default='a')
    solution_question = fields.Char(compute='compute_solution_question', readonly=True)
    solution_stripped = fields.Char(compute='compute_solution_question', readonly=True)
    solution_new_question = fields.Char()
    solution_answer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Yes/No')

    @api.depends('solution', 'article')
    def compute_solution_question(self):
        self.solution_question = None
        self.solution_stripped = None
        if self.solution:
            self.solution_stripped = self.env['solution'].compute_solution_stripped(self.solution)
            self.article = self.env['solution'].compute_article(self.solution_stripped, self.article)
            self.solution_question = self.env['solution'].compute_solution_question(self.solution_stripped, self.article)

    def confirm(self):
        if self.solution and self.solution_stripped:
            solution = self.env['solution'].search([('name', 'ilike', self.solution_stripped)], limit=1)
            if not solution:
                solution = self.env['solution'].create({'name': self.solution_stripped.title(), 'article': self.article})
            if self.challenge_id.answers:
                answers = eval(self.challenge_id.answers)
                for question_id in answers.keys():
                    answer = self.env['answer'].search([('question_id', '=', question_id), ('solution_id', '=', solution.id)], limit=1)
                    if not answer.id:
                        self.env['answer'].create({
                            'solution_id': solution.id,
                            'question_id': question_id,
                            'answer': answers[question_id]
                        })
            question = None
            if self.solution_new_question and self.solution_answer:
                question_stripped = self.solution_new_question.replace('?', '')
                question = self.env['question'].search([('name', 'ilike', question_stripped)], limit=1)
                if not question.id:
                    question = self.env['question'].create({'name': self.solution_new_question.replace('?', '')})
                answer = self.env['answer'].search([('question_id', '=', question.id), ('solution_id', '=', solution.id)], limit=1)
                if not answer.id:
                    self.env['answer'].create({
                        'solution_id': solution.id,
                        'question_id': question.id,
                        'answer': self.solution_answer
                    })
            if question and question.id:
                context = dict(
                    self.env.context,
                    default_challenge_id=self.challenge_id.id,
                    default_solution_id=solution.id,
                    default_question_id=question.id
                )
                return {
                    "name": "Help me learn!",
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": "get.answers.wizard",
                    "target": "new",
                    "binding_model_id": "challenge",
                    "binding_view_types": "form",
                    "context": context,
                }
        self.challenge_id.start_over()
        return
