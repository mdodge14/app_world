# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _


class GetAnswersWizard(models.TransientModel):
    _name = 'get.answers.wizard'
    _description = 'Get Answers Wizard'

    challenge_id = fields.Many2one('challenge')
    solution_id = fields.Many2one('solution')
    question_id = fields.Many2one('question', readonly=True)
    question = fields.Char(compute='compute_solutions')
    solution1 = fields.Char('solution', compute='compute_solutions')
    solution2 = fields.Char('solution', compute='compute_solutions')
    solution3 = fields.Char('solution', compute='compute_solutions')
    solution4 = fields.Char('solution', compute='compute_solutions')
    solution5 = fields.Char('solution', compute='compute_solutions')
    answer1 = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    answer2 = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    answer3 = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    answer4 = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    answer5 = fields.Selection([('yes', 'Yes'), ('no', 'No')])

    @api.depends('question_id', 'solution_id', 'challenge_id')
    def compute_solutions(self):
        self.solution1 = None
        self.solution2 = None
        self.solution3 = None
        self.solution4 = None
        self.solution5 = None
        self.question = self.question_id.name
        if self.challenge_id.id and self.question_id.id and self.challenge_id.answers:
            possible_solutions = self.env['solution'].search([('id', '!=', self.solution_id.id)])
            possible_solution_ids = possible_solutions.ids
            answers = eval(self.challenge_id.answers) if self.challenge_id.answers else {}
            for question_id in answers:
                for solution in possible_solutions:
                    answer = self.env['answer'].search([('question_id', '=', question_id), ('solution_id', '=', solution.id)], limit=1)
                    if answer.id and answer.answer != answers[question_id] and solution.id in possible_solution_ids:
                        possible_solution_ids.remove(solution.id)
                if len(possible_solution_ids) <= 5:
                    break
            if len(possible_solution_ids) > 0:
                self.solution1 = self.get_solution_label(possible_solution_ids[0])
            if len(possible_solution_ids) > 1:
                self.solution2 = self.get_solution_label(possible_solution_ids[1])
            if len(possible_solution_ids) > 2:
                self.solution3 = self.get_solution_label(possible_solution_ids[2])
            if len(possible_solution_ids) > 3:
                self.solution4 = self.get_solution_label(possible_solution_ids[3])
            if len(possible_solution_ids) > 4:
                self.solution5 = self.get_solution_label(possible_solution_ids[4])

    def get_solution_label(self, solution_id):
        solution = self.env['solution'].browse(solution_id)
        article = solution.article.title() + ' ' if solution.article else ''
        solution_name = solution.name.title() if (not solution.article or solution.article == 'the') else solution.name.lower()
        return '{}{}'.format(article, solution_name)

    def record_answer(self, solution_name, answer):
        if solution_name and answer:
            if solution_name[0:2].lower() == 'a ':
                solution_name = solution_name[2:]
            elif solution_name[0:3].lower() == 'an ':
                solution_name = self.solution_stripped[3:].lower()
            elif solution_name[0:4].lower() == 'the ':
                solution_name = solution_name[4:]
            solution = self.env['solution'].search([('name', 'ilike', solution_name)], limit=1)
            self.env['answer'].create({
                'solution_id': solution.id,
                'question_id': self.question_id.id,
                'answer': answer
            })

    def confirm(self):
        self.record_answer(self.solution1, self.answer1)
        self.record_answer(self.solution2, self.answer2)
        self.record_answer(self.solution3, self.answer3)
        self.record_answer(self.solution4, self.answer4)
        self.record_answer(self.solution5, self.answer5)
        self.challenge_id.start_over()
        return
