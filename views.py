from . import models
from ._builtin import Page, WaitPage


class Introduction(Page):
    #wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number == 1


class Guess(Page):
    form_model = models.Player
    form_fields = ['guess']


class ResultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        self.group.set_payoffs()


class Results(Page):

    def vars_for_template(self):
        sorted_guesses = sorted(p.guess for p in self.group.get_players())

        return {
            'sorted_guesses': sorted_guesses,
            'average': self.group.average
        }

    def before_next_page(self):

        # pass payoff to new var
        self.player.round_payoff = self.player.payoff

page_sequence = [Introduction,
                 Guess,
                 ResultsWaitPage,
                 Results]
