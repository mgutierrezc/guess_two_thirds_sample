from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c,
)

doc = """
a.k.a. Keynesian beauty contest.

Players all guess a number; whoever guesses closest to
2/3 of the average wins.

See https://en.wikipedia.org/wiki/Guess_2/3_of_the_average
"""


class Constants(BaseConstants):
    players_per_group = 8     #poner 8 o 16

    num_rounds = 8

    name_in_url = 'guess_two_thirds'

    jackpot = c(20)

    guess_max = 100

    instructions_template = 'guess_two_thirds/Instructions.html'


class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            self.group_randomly()
        else:
            self.group_like_round(1)
    
    def vars_for_admin_report(self):
        average_number = 0
        num_groups = len(self.get_groups())
        all_guesses = []
        min_guess = 0
        max_guess = 0
        for g in self.get_groups():
            average_number += g.average/num_groups
            
            for p in g.get_players():
                if p.guess != None:
                    all_guesses.append(p.guess)
            
            if len(all_guesses) != 0:
                min_guess = min(all_guesses)
                max_guess = max(all_guesses)
            
        return {
            'avg_num': round(average_number, 2),
            'min_guess': min_guess,
            'max_guess': max_guess,
        }
    

class Group(BaseGroup):
    two_thirds_avg = models.FloatField()
    average = models.FloatField(initial=0)
    best_guess = models.PositiveIntegerField()
    num_winners = models.PositiveIntegerField()



    def set_payoffs(self):
        players = self.get_players()
        guesses = [p.guess for p in players]
        self.average = sum(guesses) / len(players)
        two_thirds_avg = (2 / 3) * self.average
        self.two_thirds_avg = round(two_thirds_avg, 2)

        self.best_guess = min(guesses,
            key=lambda guess: abs(guess - self.two_thirds_avg))

        winners = [p for p in players if p.guess == self.best_guess]
        self.num_winners = len(winners)

        for p in winners:
            p.is_winner = True
            p.payoff = Constants.jackpot / self.num_winners

    def two_thirds_avg_history(self):
        return [g.two_thirds_avg for g in self.in_previous_rounds()]


class Player(BasePlayer):

    round_payoff = models.CurrencyField()

    def role(self):
        if self.id_in_group == 1:
            return 'A'
        elif self.id_in_group == 2:
            return 'B'
        elif self.id_in_group == 3:
            return 'C'
        else:
            return 'D'

    guess = models.PositiveIntegerField(max=Constants.guess_max)
    is_winner = models.BooleanField(initial=False)
