class Hearthstone:

    # Abstract class intended to contain hearthstone properties that many classes need access to
    # Basically working as a container for constants about the game itself
    # --> rarities is a great example of this, now accessable through Hearthstone.rarities
    rarities = ['common', 'rare', 'epic', 'legendary',
                'golden_common', 'golden_rare', 'golden_epic', 'golden_legendary']
    default_pack = {'common': 4, 'rare': 1, 'epic': 0, 'legendary': 0,
                    'golden_common': 0, 'golden_rare': 0, 'golden_epic': 0, 'golden_legendary': 0}
    disenchant_values = {'common': 5, 'rare': 20, 'epic': 100, 'legendary': 400,
                         'golden_common': 50, 'golden_rare': 100, 'golden_epic':400, 'golden_legendary':1600}
    enchant_values = {'common': 40, 'rare': 100, 'epic': 400, 'legendary': 1600,
                      'golden_common': 400, 'golden_rare': 800, 'golden_epic': 1600, 'golden_legendary': 3200}
    # TODO: perhaps card_sets belongs in here too, something like Hearthstone.standard_sets / wild_set / all_sets