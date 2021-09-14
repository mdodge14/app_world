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
            return http.request.render('world_of_questions.game_play', {'challenge': challenge})
        return request.redirect("/{}/o".format(challenge_id))


class AppWebsiteController(http.Controller):

    @http.route(['/'], type='http', auth="public", website=True, sitemap=False)
    def play(self):
        challenge = request.env['challenge'].with_user(SUPERUSER_ID).create({'name': 'Hi there!'})
        return http.request.render('world_of_questions.game_play', {'challenge': challenge})
