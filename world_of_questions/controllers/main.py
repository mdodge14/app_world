# -*- coding: utf-8 -*-
import logging
from odoo.http import request
from odoo import http, _, SUPERUSER_ID
from odoo.addons.web.controllers.main import Home

_logger = logging.getLogger(__name__)


class AppWebsite(Home):

    @http.route('/<int:challenge_id>/<string:answer>', type='http', auth="public", website=True, sitemap=True)
    def index(self, challenge_id, answer=None):
        if challenge_id:
            challenge = request.env['challenge'].with_user(SUPERUSER_ID).search([('id', '=', challenge_id)], limit=1)
        if not challenge.id:
            challenge = request.env['challenge'].with_user(SUPERUSER_ID).create({'name': 'Hi there!'})
        if answer == 'yes':
            challenge.yes_action()
        elif answer == 'no':
            challenge.no_action()
        elif answer in ('sometimes', 'kindof'):
            challenge.ask_next_question(answer)
        elif answer == 'unknown':
            challenge.ask_next_question()
        elif answer == 'guessed':
            challenge.solution_found()
        elif answer == 'r':
            challenge.start_over()
        else:
            if challenge.is_out_of_questions:
                return http.request.render('world_of_questions.get_solution', {'challenge': challenge})
            return http.request.render('world_of_questions.game_play', {'challenge': challenge})
        return request.redirect("/{}/o".format(challenge_id))

    @http.route(['/solution'], type='http', auth="public", website=True, sitemap=False)
    def add_solution(self, **post):
        challenge = request.env['challenge'].with_user(SUPERUSER_ID).search([('id', '=', post.get('challenge_id'))], limit=1)
        if post.get('solution') and post.get('question'):
            get_solution_wizard = request.env['get.solution.wizard'].with_user(SUPERUSER_ID).create({
                'challenge_id': int(post.get('challenge_id')),
                'solution': post.get('solution'),
                'article': post.get('article_select'),
                'solution_new_question': post.get('question'),
                'solution_answer': 'no' if post.get('answer-radio') == 'answer_no' else 'yes'
            })
            if get_solution_wizard.confirm():
                challenge.start_over()
                return request.redirect("/{}/o".format(challenge.id))
        else:
            challenge.start_over()
        return request.redirect("/{}/o".format(challenge.id))


class AppWebsiteController(http.Controller):

    @http.route(['/'], type='http', auth="public", website=True, sitemap=False)
    def play(self):
        challenge = request.env['challenge'].with_user(SUPERUSER_ID).create({'name': 'Hi there!'})
        return http.request.render('world_of_questions.game_play', {'challenge': challenge})
