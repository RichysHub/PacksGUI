

class Dust:
    # Dust bottle reward
    def __init__(self, min_dust, max_dust):
        self.min_dust = min_dust
        self.max_dust = max_dust


class Gold:
    # Gold bag reward
    def __init__(self, min_gold, max_gold):
        self.min_gold = min_gold
        self.max_gold = max_gold


class Pack:
    # Single pack reward, of latest expansion
    pass


class Card:
    # Single card reward
    def __init__(self, min_rarity, max_rarity=None):
        self.min_rarity = min_rarity
        if max_rarity:
            self.max_rarity = max_rarity
        else:
            self.max_rarity = self.min_rarity


class Random:
    # Denotes a random reward, from Reward.pool
    pass


class Reward:
    def __init__(self, wins, number, guaranteed, pool):
        self.wins = wins
        self.number = number
        self.guaranteed = guaranteed
        self.pool = pool


class Hearthstone:

    # Abstract class intended to contain hearthstone properties that many classes need access to
    # Basically working as a container for constants about the game itself
    # --> rarities is a great example of this, now accessable through Hearthstone.rarities

    # TODO: perhaps separate names rarities, for UI pieces
    rarities = ['common', 'rare', 'epic', 'legendary',
                'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']
    rarity_display_names = dict(zip(rarities, ['Common', 'Rare', 'Epic', 'Legendary',
                                               'Golden Common', 'Golden Rare', 'Golden Epic', 'Golden Legendary']))

    # TODO: maybe these things should use a dict(zip()), so rarity names are only in 1 place
    default_pack = {'common': 4, 'rare': 1, 'epic': 0, 'legendary': 0,
                    'golden_common': 0, 'golden_rare': 0, 'golden_epic': 0, 'golden_legendary': 0}
    disenchant_values = {'common': 5, 'rare': 20, 'epic': 100, 'legendary': 400,
                         'golden_common': 50, 'golden_rare': 100, 'golden_epic':400, 'golden_legendary':1600}
    enchant_values = {'common': 40, 'rare': 100, 'epic': 400, 'legendary': 1600,
                      'golden_common': 400, 'golden_rare': 800, 'golden_epic': 1600, 'golden_legendary': 3200}
    # TODO: perhaps card_sets belongs in here too, something like Hearthstone.standard_sets / wild_set / all_sets

    # Might want to get key names for presentation sake. arena_keys[n] gives name of key for n wins
    arena_keys = ['Novice', 'Apprentice', 'Journeyman', 'Copper', 'Silver', 'Gold', 'Platinum',
            'Diamond', 'Champion', 'Ruby', 'Frostborn', 'Molten', 'Lightforge']

    # Number of boxes your arena reward will contain. num_arena_rewards[3]
    num_arena_rewards = [2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5]

    # Todo: inclusion of 'common' etc seems like a great source for bugs, perhaps replace
    # Perhaps even an enum?
    # Rewards are correct to gamepedia, prior to Aug11 patch (made single common cards less frequent)
    # (may have been removed from some tiers)

    # Usage is that ArenaMiniView can look up rewards[wins],
    # pull number of boxes to create, and create them,
    # pull list of guaranteed, and populate those boxes,
    # pull list of pool, make dropdown for remaining boxes
    rewards = {
        0: Reward(0, num_arena_rewards[0], (Pack(), Random()),
                  (Gold(25, 40), Dust(25, 40), Card('common'))),
        1: Reward(1, num_arena_rewards[1], [Pack(), Random()],
                  [Gold(30, 50), Dust(25, 50), Card('common'), Pack()]),
        2: Reward(2, num_arena_rewards[2], [Pack(), Random()],
                  [Gold(35, 60), Dust(40, 50), Card('common', 'rare'), Pack()]),
        3: Reward(3, num_arena_rewards[3], [Pack(), Gold(25, 35), Random()],
                  [Gold(20, 25), Dust(20, 25), Card('common', 'rare'), Pack()]),
        4: Reward(4, num_arena_rewards[4], [Pack(), Gold(40, 60), Random()],
                  [Gold(20, 30), Dust(20, 25), Card('common', 'rare'), Pack()]),
        5: Reward(5, num_arena_rewards[5], [Pack(), Gold(45, 60), Random()],
                  [Gold(45, 60), Dust(45, 60), Card('common', 'rare'), Pack()]),
        6: Reward(6, num_arena_rewards[6], [Pack(), Gold(75, 85), Random()],
                  [Gold(45, 60), Dust(45, 60), Card('common', 'rare'), Pack()]),
        7: Reward(7, num_arena_rewards[7], [Pack(), Gold(150, 160), Random()],
                  [Gold(20, 30), Dust(20, 25), Card('common', 'rare'), Pack()]),
        8: Reward(8, num_arena_rewards[8], [Pack(), Gold(150, 160), Random(), Random()],
                  [Gold(20, 45), Dust(20, 25), Card('common', 'golden_legendary'), Pack()]),
        9: Reward(9, num_arena_rewards[9], [Pack(), Gold(150, 165), Random(), Random()],
                  [Gold(20, 120), Dust(20, 50), Card('common', 'golden_legendary'), Pack()]),
        10: Reward(10, num_arena_rewards[10], [Pack(), Gold(150, 185), Random(), Random()],
                  [Gold(65, 125), Dust(65, 95), Card('rare', 'golden_legendary'), Pack()]),
        11: Reward(11, num_arena_rewards[11], [Pack(), Gold(195, 210), Random(), Random()],
                  [Gold(65, 205), Dust(60, 95), Card('rare', 'golden_legendary'), Pack()]),
        12: Reward(12, num_arena_rewards[12], [Pack(), Gold(215, 225), Gold(25, 35), Random(), Random()],
                  [Gold(65, 185), Card('epic', 'golden_legendary'), Pack()])
    }

    classes = ['Druid', 'Hunter', 'Mage', 'Paladin', 'Priest', 'Rogue', 'Shaman', 'Warlock', 'Warrior']
