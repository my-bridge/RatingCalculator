from prettytable import PrettyTable
import pdb
class RatingCalculator(object):
    def __init__(self):
        self.players = PlayerList()

    def add_player(self, player):
        if player not in self.players:
            self.players.add_player(player)

    def add_ergebnis(self, liste):
        name = liste[0]
        hands = liste[1]
        imps_lost = liste[2]
        # self.add_player(name)
        self.update_rating(name, hands, imps_lost)

    def update_rating(self, name, hands, imps_lost):
        self.players.update_rating(name, hands, imps_lost)

    def get_rating_from_name(self, name):
        if self.players.check_player_in_list(name) == True:
            self.players.liste[name].display_player()
        else:
            print "Player not rated!"

    def show_rating(self):
        self.players.display_rating()

class Player(object):
    def __init__(self, name):
        self.name = name
        self.HIGHEST_RATING = 3400
        self.K_INITIAL = 48
        self.K_GM = 16
        self.K_OTHER = 24
        self.K_CLASSIFIER_BOUNDARY = 2500
        self.INITIAL_RATING = 2200
        self.INITIAL_RATING_NO_BATCHES = 30
        self.BATCH = 12
        self.rating_dict = {}
        self.rating_dict["old_rating"] = self.INITIAL_RATING
        self.rating_dict["k_factor"] = self.K_INITIAL
        self.rating_dict["hands_left"] = 0
        self.rating_dict["imps_lost_left"] = 0
        self.rating_dict["no_batches"] = 0
        self.rating_dict["gm_rating"] = False

    def display_player(self):
        print "Name: ", self.name
        old, hands, imps, k, no =  self.get_rating()
        table = PrettyTable(["Name", "Rating", "Hands left", "IMPS lost left", "Current k-factor", "No. Batches"])
        table.add_row([self.name, old, hands, imps, k, no])
        print table

    def get_rating(self):
        return self.rating_dict["old_rating"], self.rating_dict["hands_left"],\
            self.rating_dict["imps_lost_left"], self.rating_dict["k_factor"],\
            self.rating_dict["no_batches"]

    def calculate_new_rating(self, hands, imps_lost_new):
        if hands == 0:
            return
        imps_avg = float(imps_lost_new) / float(hands)
        # print "imps_avg: ", imps_avg

        if self.rating_dict["hands_left"] > 0:
            fill_up = self.BATCH - self.rating_dict["hands_left"]
            # print "fill_up: ", fill_up
            hands = hands - fill_up
            # print "needed hands: ", hands
            imps_lost_fill_up = self.rating_dict["imps_lost_left"] + float(fill_up) * imps_avg
            # print "imps_lost_fill_up", imps_lost_fill_up
            self.get_new_rating_one_batch(imps_lost_fill_up)

        while hands > 0:
            if hands < self.BATCH:
                self.rating_dict["hands_left"] = hands
                self.rating_dict["imps_lost_left"] = float(hands) * imps_avg
                hands = 0
                return
            lost = self.BATCH * imps_avg
            self.get_new_rating_one_batch(lost)
            # self.add_batch()
            hands -= self.BATCH

    def get_new_rating_one_batch(self, imps_lost):
        # pdb.set_trace()
        exp_performance = float(self.HIGHEST_RATING - self.old_rating) / 1000.0
        # print "exp_performance: ", exp_performance
        performance = float(imps_lost) / float(self.BATCH)
        # print "performance: ", performance
        rating_new = self.old_rating + self.k * (exp_performance - performance)
        # print "rating_new: ", rating_new
        self.rating_dict["old_rating"] = rating_new
        self.add_batch()
        return

    @property
    def old_rating(self):
        return self.rating_dict["old_rating"]

    def add_batch(self):
        self.rating_dict["no_batches"] += 1
        self.change_k()

    @property
    def k(self):
        return self.rating_dict["k_factor"]

    def change_k(self):
        if self.rating_dict["old_rating"] >= self.K_CLASSIFIER_BOUNDARY:
            self.rating_dict["gm_rating"] = True

        if self.rating_dict["no_batches"] <= self.INITIAL_RATING_NO_BATCHES:
            self.rating_dict["k_factor"] = self.K_INITIAL
            return
        if self.rating_dict["gm_rating"] == True:
            self.rating_dict["k_factor"] = self.K_GM
            return
        else:
            self.rating_dict["k_factor"] = self.K_OTHER
            return



class PlayerList(object):
    def __init__(self):
        self.liste = {}

    def add_player(self, player_string):
        if player_string in self.liste:
            return
        else:
            player = Player(player_string)
            self.liste[player_string] = player

    def get_player(self, player_string):
        if player_string in self.liste:
            return self.liste[player_string]
        else:
            self.add_player(player_string)
            return self.liste[player_string]

    def check_player_in_list(self, player_string):
        if player_string in self.liste:
            return True
        return False


    def update_rating(self, name, hands, imps_lost):
        if name in self.liste:
            # print self.liste[name]
            pass
        else:
            print "Name not included"
        player = self.get_player(name)
        player.calculate_new_rating(hands, imps_lost)
        # print player.display_player()


    def display_rating(self):
        table = PrettyTable(["Rank", "Name", "Rating", "Hands left", "IMPS lost left", "Current k-factor", "No. Batches"])
        table.sortby = "Rating"
        table.reversesort = True
        pos = 1
        tr = self.liste
        global tr
        xr = sorted(self.liste, key = lambda x : tr[x].get_rating()[0], reverse = True)
        for player in xr:
            rating, hands_left, imps_left, k, batches = self.liste[player].get_rating()
            table.add_row([pos, player, rating, hands_left, imps_left, k, batches])
            pos += 1
        print table.get_string(sortby = "Rating", reversesort = True)

class Test(object):
    def __init__(self):
        pass
    def do(self):
        """ results for game over from Sep 2020 to Aug 2023
        shown month-wise
        input: (hands, IMPs-lost-tuples) for each month
        output: rating
        """
        results_game_over = [

(93, 73),
(95, 93),
(284, 149),
(86, 83),
(110, 115),
(183, 116),
(115, 145),
(244, 214),
(83, 53),
(12, 2),
(61, 62),
(16, 20),
(20, 7),
(30, 39),
(34, 21),
(165, 122),
(148, 96),
(50, 42),
(85, 80),
(208, 181),
(32, 10),
(24, 5),
(13, 1),
(36, 42),
(52, 18),
(13, 14),
(23, 7),
(32, 23),
(23, 15),
]




        new = RatingCalculator()
        results_new = [("game over", c[0], c[1]) for c in results_game_over]
        for element in results_new:
            new.add_ergebnis(element)
            new.show_rating()

if __name__ == "__main__":
    t = Test()
    t.do()

