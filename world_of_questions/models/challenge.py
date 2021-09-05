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
    message = fields.Char(default="Would you like to play 20 questions?", readonly=True)
    question_id = fields.Many2one('question', string='Question')
    asked_question_ids = fields.Many2many('question', 'challenge_asked_questions', 'cid', 'qid')
    possible_solutions = fields.Many2many('solution', 'challenge_possible_solutions', 'cid', 'sid')

    # TODO: If guessed solution, capture any learned answers
    # TODO: If reached 20 questions, message "lost" and ask for solution, then a question that would have been good to ask with the answer
    def yes_action(self):
        if self.state in ('new', 'not playing', 'done'):
            self.message = "Great! I'll be the guesser. Do you know what you are?"
            self.state = 'ready'
        elif self.state == 'ready':
            self.ask_next_question()
        elif self.state == 'ask':
            self.eliminate_solutions('yes')
            if not self.check_for_solution_question('yes'):
                self.ask_next_question()

    def no_action(self):
        if self.state in ('new', 'ready', 'done'):
            self.message = "OK, no problem. I'll be here when you're ready to play."
            self.state = 'not playing'
        elif self.state == 'ask':
            self.eliminate_solutions('no')
            if not self.check_for_solution_question('no'):
                self.ask_next_question()

    def start_over(self):
        self.state = 'new'
        self.name = "Hi there!"
        self.message = "Would you like to play 20 questions?"
        self.asked_question_ids = [(5, 0, 0)]
        self.possible_solutions = self.env['solution'].search([])

    def eliminate_solutions(self, yes_or_no):
        remove = []
        for solution in self.possible_solutions:
            answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('solution_id', '=', solution.id)], limit=1)
            if answer.id and answer.answer != yes_or_no:
                remove.append(solution.id)
        for r in remove:
            self.possible_solutions = [(3, r, 0)]

    def get_remaining_questions(self):
        if self.asked_question_ids:
            questions = self.env['question'].search([('id', 'not in', self.asked_question_ids.ids)], order='sequence asc')
        else:
            questions = self.env['question'].search([], order='sequence asc')
        return questions

    def check_for_solution_question(self, yes_or_no):
        remaining_questions = self.get_remaining_questions()
        for solution in self.possible_solutions:
            answer = self.env['answer'].search([('question_id', '=', self.question_id.id), ('solution_id', '=', solution.id), ('answer', '=', yes_or_no)], limit=1)
            if answer.id:
                new_answer = self.env['answer'].search([('solution_id', '=', solution.id), ('question_id', 'in', remaining_questions.ids)], limit=1)
                if new_answer.id:
                    self.ask_question(new_answer.question_id)
                    return True
        else:
            return False

    def ask_next_question(self):
        questions = self.get_remaining_questions()
        if len(questions) > 1:
            yes_answers = {}
            no_answers = {}
            for question in questions:
                for solution in self.possible_solutions:
                    answer = self.env['answer'].search([('question_id', '=', question.id), ('solution_id', '=', solution.id)], limit=1)
                    if answer.id:
                        if answer.answer == 'yes':
                            if question.id in yes_answers:
                                yes_answers[question.id] += 1
                            else:
                                yes_answers[question.id] = 1
                        elif answer.answer == 'no':
                            if question.id in no_answers:
                                no_answers[question.id] += 1
                            else:
                                no_answers[question.id] = 1

            best_question = questions[0]
            best_number_eliminated = 0
            if best_question.id in yes_answers and best_question.id in no_answers and yes_answers[question.id] >= no_answers[question.id]:
                best_number_eliminated = no_answers[question.id]
            elif best_question.id in yes_answers and best_question.id in no_answers and yes_answers[question.id] < no_answers[question.id]:
                best_number_eliminated = no_answers[question.id]
            for question in questions:
                if question.id != best_question.id:
                    number_eliminated = 0
                    if question.id in yes_answers and question.id in no_answers and yes_answers[question.id] >= no_answers[question.id]:
                        number_eliminated = no_answers[question.id]
                    elif question.id in yes_answers and question.id in no_answers and yes_answers[question.id] < no_answers[question.id]:
                        number_eliminated = no_answers[question.id]
                    if number_eliminated > best_number_eliminated:
                        best_question = question
                        best_number_eliminated = number_eliminated
        else:
            best_question = questions[0]
        self.ask_question(best_question)

    def ask_question(self, question):
        self.question_id = question.id
        self.asked_question_ids = [(4, self.question_id.id)]
        number = len(self.asked_question_ids) if self.asked_question_ids else 1
        self.name = "Question #{}".format(number)
        self.message = "{}?".format(self.question_id.name)
        self.state = 'ask'

    def solution_found(self):
        self.state = 'done'
        self.name = "I knew it!"
        self.message = "Would you like to play again?"
        self.asked_question_ids = [(5, 0, 0)]
        self.possible_solutions = self.env['solution'].search([])

