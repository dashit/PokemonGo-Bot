import operator
from collections import defaultdict
from pokemongo_bot import logger
from time import sleep


pokemon_name_to_family_id = {
    'abra': 63,
    'aerodactyl': 142,
    'articuno': 144,
    'bellsprout': 69,
    'weepinbell': 69,
    'bulbasaur': 1,

    'caterpie': 10,
    'metapod': 10,

    'chansey': 113,
    'charmander': 4,

    'clefairy': 35,
    'clefable': 35,

    'cubone': 104,
    'diglett': 50,
    'ditto': 132,

    'doduo': 84,
    'dodrio': 84,

    'dratini': 147,
    'dragonair': 147,
    'dragonite': 147,

    'drowzee': 96,
    'hypno': 96,
    'eevee': 133,
    'ekans': 23,
    'electabuzz': 125,
    'exeggcute': 102,
    'exeggutor': 102,
    'farfetchd': 83,

    'gastly': 92,
    'haunter': 92,
    'gengar': 92,

    'geodude': 74,
    'graveler': 74,

    'goldeen': 118,
    'seaking': 118,

    'grimer': 88,
    'growlithe': 58,
    'hitmonchan': 107,
    'hitmonlee': 106,

    'horsea': 116,
    'seadra': 116,

    'jigglypuff': 39,
    'wigglytuff': 39,

    'jynx': 124,
    'kabuto': 140,
    'kangaskhan': 115,
    'koffing': 109,

    'krabby': 98,
    'kingler': 98,

    'lapras': 131,
    'lickitung': 108,
    'machop': 66,
    'magikarp': 129,
    'magmar': 126,

    'magnemite': 81,
    'magneton': 81,

    'mankey': 56,

    'meowth': 52,
    'persian': 52,

    'mew': 151,
    'mewtwo': 150,
    'moltres': 146,
    'mr_mime': 122,
    'nidoran': 29,
    'nidorina': 29,
    'nidoran2': 32,
    'nidorino': 32,

    'oddish': 43,
    'gloom': 43,

    'omanyte': 138,
    'onix': 95,
    'paras': 46,
    'parasect': 46,

    'pidgey': 16,
    'pidgeotto': 16,
    'pidgeot': 16,

    'pikachu': 25,
    'pinsir': 127,
    'poliwag': 60,
    'poliwhirl': 60,

    'ponyta': 77,
    'rapidash': 77,

    'porygon': 137,
    'psyduck': 54,
    'golduck': 54,

    'rattata': 19,
    'raticate': 19,

    'rhyhorn': 111,
    'sandshrew': 27,
    'sandslash': 27,
    'scyther': 123,
    'seel': 86,
    'dewgong': 86,
    'shellder': 90,
    'cloyster': 90,

    'slowpoke': 79,
    'slowbro': 79,

    'snorlax': 143,

    'spearow': 21,
    'fearow': 21,

    'squirtle': 7,
    'wartortle': 7,

    'staryu': 120,
    'starmie': 120,

    'tangela': 114,
    'tauros': 128,

    'tentacool': 72,
    'tentacruel': 72,

    'venonat': 48,
    'venomoth': 48,

    'electrode': 100,
    'voltorb': 100,

    'vulpix': 37,

    'weedle': 13,
    'kakuna': 13,

    'zapdos': 145,

    'zubat': 41,
    'golbat': 41,
}

candies_to_evolve = {
    'bellsprout': None,  # 25 # switch me
    'caterpie': None,  # 12 switch me
    'clefable': None,
    'clefairy': 50,
    'cloyster': None,
    'diglett': 50,
    'dodrio': None,
    'doduo': 50,
    'dratini': 25,
    'drowzee': 50,
    'ekans': 50,
    'electrode': None,
    'exeggcute': 50,
    'fearow': None,
    'gastly': None, # 25 # switch me
    'geodude': None, #25,
    'gloom': 100,
    'golbat': None,
    'goldeen': 50,
    'grimer': 50,
    'haunter': 100,
    'horsea': 50,
    'jigglypuff': 50,
    'kakuna': None,
    'kingler': None,
    'koffing': 50,
    'krabby': 50,
    'machop': None,
    'magikarp': None,
    'magmar': None,
    'magnemite': 50,
    'magneton': None,
    'meowth': 50,
    'metapod': None,
    'nidoran': None,
    'nidoran2': None,
    'nidorina': None,
    'oddish': None, #25 switch me
    'paras': 50,
    'parasect': None,
    'persian': 50,
    'pidgeotto': 50,
    'pidgey': 12,
    'pikachu': None,
    'pinsir': None,
    'poliwag': None,
    'ponyta': 50,
    'psyduck': 50,
    'raticate': None,
    'rattata': 25,
    'rhyhorn': 50,
    'sandshrew': 50,
    'seadra': None,
    'seaking': None,
    'seel': 50,
    'dewgong': None,
    'shellder': 50,
    'slowpoke': 50,
    'spearow': 50,
    'staryu': 50,
    'tangela': None,
    'tentacool': 50,
    'tentacruel': None,
    'venomoth': 50,
    'venonat': 50,
    'voltorb': 50,
    'weedle': 12,
    'weepinbell': 100,
    'wigglytuff': None,
    'zubat': 50,
    'cubone': None,
    'bulbasaur': None,
    'squirtle': None,
    'charmander': None,
    'charmeleon': None,
    'exeggutor': None,
    'abra': None,
    'golduck': None,
    'graveler': 100,
    'growlithe': None,
    'hypno': None,
    'jynx': None,
    'kabuto': None,
    'mankey': 50,
    'pidgeot': None,
    'rapidash': None,
    'sandslash': None,
    'slowbro': None,
    'starmie': None,
    'wartortle': None,
    'dragonair': None,
    'dragonite': None,
    'gengar': None,
    'poliwhirl': None,
    'lickitung': None,
    'scyther': None,
}


class KimEvolver(object):
    def __init__(self, bot):
        self.bot = bot
        self.api = bot.api

        self.all_pokemon_list = {
            int(each['Number']): each
            for each in bot.pokemon_list
        }
        self.pokemon_name_to_id = {
            each['Name'].lower(): int(each['Number'])
            for each in bot.pokemon_list
        }

        self.pokemon_name_to_id['nidoran'] = self.pokemon_name_to_id['nidoran f']
        self.pokemon_name_to_id['nidoran2'] = self.pokemon_name_to_id['nidoran m']

    def emit_event(self, event, sender=None, level='info', formatted='',
                   data={}):
        if not sender:
            sender = self
        self.bot.event_manager.emit(
            event,
            sender=sender,
            level=level,
            formatted=formatted,
            data=data
        )

    def pokemon_potential(self, pokemon_data):
        total_iv = 0
        iv_stats = ['individual_attack', 'individual_defense', 'individual_stamina']

        for individual_stat in iv_stats:
            try:
                total_iv += pokemon_data[individual_stat]
            except:
                pokemon_data[individual_stat] = 0
                continue

        return round((total_iv / 45.0), 2)

    def get_my_pokemon(self, inventory_response):
        items = inventory_response['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        my_pokemon_list = []

        for item in items:
            if 'pokemon_data' in item['inventory_item_data']:
                pokemon = item['inventory_item_data']['pokemon_data']
                pokemon['iv'] = self.pokemon_potential(pokemon)
                my_pokemon_list.append(pokemon)

        pokemon_by_species = defaultdict(list)
        for pokemon in my_pokemon_list:
            if 'pokemon_id' in pokemon:
                # not an egg
                pokemon_by_species[pokemon['pokemon_id']].append(pokemon)

        pokemon_by_species2 = {}
        for species, pokemons in pokemon_by_species.items():
            pokemon_by_species2[species] = sorted(
                pokemons, key=operator.itemgetter('iv'), reverse=True,
            )

        return pokemon_by_species2

    def get_candies(self, inventory_response):
        items = inventory_response['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        candy_by_family = {}
        for item in items:
            if 'candy' in item['inventory_item_data']:
                item2 = item['inventory_item_data']['candy']
                candy_by_family[item2['family_id']] = item2['candy']

        return candy_by_family

    def release_or_evolve(self, initial=False):
        request = self.bot.api.create_request()
        request.get_player()
        request.get_inventory()
        response = request.call()

        candy_by_family = self.get_candies(response)
        my_pokemon = self.get_my_pokemon(response)

        for pokemon_name, candy_for_upgrade in candies_to_evolve.items():
            candies_needed_for_evolve = candies_to_evolve.get(pokemon_name, False)
            if candies_needed_for_evolve is False:
                if initial:
                    self.emit_event(
                        'no_candy_info',
                        formatted='No candy information found for {pokemon}.',
                        data={'pokemon': pokemon_name}
                    )
                continue
            family_id = pokemon_name_to_family_id.get(pokemon_name)
            if not family_id:
                if initial:
                    self.emit_event(
                        'no_candy_info',
                        formatted='No family information found for {pokemon}.',
                        data={'pokemon': pokemon_name}
                    )
                continue

            candies_available = candy_by_family.get(family_id)

            pokemons_in_species = my_pokemon.get(self.pokemon_name_to_id[pokemon_name], [])

            if candies_available is None or candies_needed_for_evolve is None:
                amount_of_upgrades = 0
            else:
                amount_of_upgrades = int(candies_available / candies_needed_for_evolve)

            iteration = 0
            for pokemon in pokemons_in_species:
                pokemon_id = pokemon['id']

                if iteration < amount_of_upgrades:
                    self.emit_event(
                        'evolving_pokemon',
                        formatted='Evolving {pokemon} (iv {iv})',
                        data={'pokemon': pokemon_name, 'iv': pokemon['iv']}
                    )
                    self.api.evolve_pokemon(pokemon_id=pokemon_id)
                    sleep(20 if initial else 1)
                elif iteration == amount_of_upgrades:
                    pass  # keeping
                else:
                    self.emit_event(
                        'releasing_pokemon',
                        formatted='Releasing {pokemon} (iv {iv})',
                        data={'pokemon': pokemon_name, 'iv': pokemon['iv']}
                    )
                    self.api.release_pokemon(pokemon_id=pokemon_id)
                    sleep(1 if initial else 0.1)
                iteration += 1

        eevees = my_pokemon.get(pokemon_name_to_family_id['eevee'], [])
        iteration = 0
        for pokemon in eevees:
            pokemon_id = pokemon['id']

            if iteration < 3:
                # keeping
                pass
            else:
                self.emit_event(
                    'releasing_pokemon',
                    formatted='Releasing {pokemon} (iv {iv})',
                    data={'pokemon': 'eevee', 'iv': pokemon['iv']}
                )
                self.api.release_pokemon(pokemon_id=pokemon_id)
                sleep(1 if initial else 0.1)
            iteration += 1

        ##############################################


        # for pokemon_name, candy_for_upgrade in candies_to_evolve.items():
        #     print 'handling {} ({} candies)'.format(pokemon_name, candy_for_upgrade)
        #     pokemon_id = pokemon_name_to_id[pokemon_name]
        #     pokemons = pokemon_by_species.get(pokemon_id)
        #     if not pokemons:
        #         print('  did not find pokemon {} (#{}) in inventory'.format(
        #             pokemon_name, pokemon_id))
        #         continue
        #     current_candy = candy_by_family.get(pokemon_id, None)
        #
        #     if current_candy is None or candy_for_upgrade is None:
        #         amount_of_upgrades = 0
        #         print('  not doing upgrades on {}'.format(pokemon_name))
        #     else:
        #         amount_of_upgrades = int(current_candy / candy_for_upgrade)
        #         if amount_of_upgrades > 0:
        #             print(
        #             '  can do {} upgrades for {}'.format(amount_of_upgrades,
        #                                                  pokemon_name))
        #         else:
        #             print('  cannot do  upgrades on {}'.format(pokemon_name))
        #
        #     iteration = 0
        #     for pokemon in pokemons:
        #         pokemon_id = pokemon['id']
        #
        #         if iteration < amount_of_upgrades:
        #             print '  evolving {}'.format(pokemon_id)
        #             api.evolve_pokemon(pokemon_id=pokemon_id)
        #             api.call()
        #             sleep(20)
        #         elif iteration == amount_of_upgrades:
        #             print '  keeping {}'.format(pokemon_id)
        #         else:
        #             print '  releasing {}'.format(pokemon_id)
        #             api.release_pokemon(pokemon_id=pokemon_id)
        #             api.call()
        #             sleep(1)
        #         iteration += 1
