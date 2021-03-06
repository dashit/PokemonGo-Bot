# -*- coding: utf-8 -*-

import time
from sets import Set
from utils import distance
from pokemongo_bot.human_behaviour import sleep
from pokemongo_bot import logger
import operator
from collections import defaultdict


pokemon_name_to_family_id = {
    'abra': 63,
    'aerodactyl': 142,
    'articuno': 144,
    'bellsprout': 69,
    'bulbasaur': 1,
    'caterpie': 10,
    'chansey': 113,
    'charmander': 4,
    'clefairy': 35,
    'cubone': 104,
    'diglett': 50,
    'ditto': 132,
    'doduo': 84,
    'dratini': 147,
    'drowzee': 96,
    'eevee': 133,
    'ekans': 23,
    'electabuzz': 125,
    'exeggcute': 102,
    'farfetchd': 83,
    'gastly': 92,
    'geodude': 74,
    'goldeen': 118,
    'grimer': 88,
    'growlithe': 58,
    'hitmonchan': 107,
    'hitmonlee': 106,
    'horsea': 116,
    'jigglypuff': 39,
    'jynx': 124,
    'kabuto': 140,
    'kangaskhan': 115,
    'koffing': 109,
    'krabby': 98,
    'lapras': 131,
    'lickitung': 108,
    'machop': 66,
    'magikarp': 129,
    'magmar': 126,
    'magnemite': 81,
    'mankey': 56,
    'meowth': 52,
    'mew': 151,
    'mewtwo': 150,
    'moltres': 146,
    'mr_mime': 122,
    'nidoran': 29,
    'nidoran2': 32,
    'oddish': 43,
    'omanyte': 138,
    'onix': 95,
    'paras': 46,
    'pidgey': 16,
    'pikachu': 25,
    'pinsir': 127,
    'poliwag': 60,
    'ponyta': 77,
    'porygon': 137,
    'psyduck': 54,
    'rattata': 19,
    'rhyhorn': 111,
    'sandshrew': 27,
    'scyther': 123,
    'seel': 86,
    'shellder': 90,
    'slowpoke': 79,
    'snorlax': 143,
    'spearow': 21,
    'squirtle': 7,
    'staryu': 120,
    'tangela': 114,
    'tauros': 128,
    'tentacool': 72,
    'venonat': 48,
    'voltorb': 100,
    'vulpix': 37,
    'weedle': 13,
    'zapdos': 145,
    'zubat': 41,
}

candies_to_evolve = {
    'pidgey': 12,
    'caterpie': 12,
    'weedle': 12,
    'rattata': 25,
    'squirtle': 25,
    'dratini': 25,
    'spearow': 50,
    'zubat': 50,
    'drowzee' :50,
    'venonat': 50,
    'staryu': 50,
    'sandshrew': 50,
    'meowth': 50,
    'psyduck': 50,
    'slowpoke': 50,
    'koffing': 50,
    'krabby': 50,
    'horsea': 50,
    'goldeen': 50,
    'shellder': 50,
    'jigglypuff': 50,
    'paras': 50,
    'magnemite': 50,
    'voltorb': 50,
    'clefairy': 50,
    'clefable': None,
    'wigglytuff': None,

    # switch me
    'oddish': None, #25,
    'gloom': 100,

    'parasect': None,
    'venomoth': 50,
    'persian': 50,
    'tentacool': 50,
    'tentacruel': None,
    'ponyta': 50,
    'magneton': None,
    'doduo': 50,
    'seel': 50,
    'kingler': None,
    'exeggcute': 50,
    'tangela': None,
    'seaking': None,
    'pinsir': None,

    # switch me
    'gastly': None, # 25
    'haunter': 100,

    'magikarp': 400,

    'raticate': None,
    'pidgeotto': 50,
    'golbat': None,
    'kakuna': None,
    'metapod': None,
    'fearow': None,
    'pikachu': None,
    'nidoran m': None,
    'nidoran f': None,

    'nidorina': None,
    'poliwag': None,
}


class PokemonCatchWorker(object):
    BAG_FULL = 'bag_full'
    NO_POKEBALLS = 'no_pokeballs'

    def __init__(self, pokemon, bot):
        self.pokemon = pokemon
        self.api = bot.api
        self.bot = bot
        self.position = bot.position
        self.config = bot.config
        self.pokemon_list = bot.pokemon_list
        self.item_list = bot.item_list
        self.inventory = bot.inventory

        self.all_pokemon_list = {
            int(each['Number']): each
            for each in bot.pokemon_list
        }
        self.pokemon_name_to_id = {
            each['Name'].lower(): int(each['Number'])
            for each in bot.pokemon_list
        }

    def work(self):
        encounter_id = self.pokemon['encounter_id']
        spawnpoint_id = self.pokemon['spawnpoint_id']
        player_latitude = self.pokemon['latitude']
        player_longitude = self.pokemon['longitude']
        self.api.encounter(encounter_id=encounter_id, spawnpoint_id=spawnpoint_id,
                           player_latitude=player_latitude, player_longitude=player_longitude)
        response_dict = self.api.call()

        if response_dict and 'responses' in response_dict:
            if 'ENCOUNTER' in response_dict['responses']:
                if 'status' in response_dict['responses']['ENCOUNTER']:
                    if response_dict['responses']['ENCOUNTER']['status'] is 7:
                        logger.log('[x] Pokemon Bag is full!', 'red')
                        return PokemonCatchWorker.BAG_FULL

                    if response_dict['responses']['ENCOUNTER']['status'] is 1:
                        cp = 0
                        total_IV = 0
                        if 'wild_pokemon' in response_dict['responses']['ENCOUNTER']:
                            pokemon = response_dict['responses']['ENCOUNTER']['wild_pokemon']
                            catch_rate = response_dict['responses']['ENCOUNTER']['capture_probability']['capture_probability'] # 0 = pokeballs, 1 great balls, 3 ultra balls

                            if 'pokemon_data' in pokemon and 'cp' in pokemon['pokemon_data']:
                                cp = pokemon['pokemon_data']['cp']
                                iv_stats = ['individual_attack', 'individual_defense', 'individual_stamina']

                                for individual_stat in iv_stats:
                                    try:
                                        total_IV += pokemon['pokemon_data'][individual_stat]
                                    except:
                                        pokemon['pokemon_data'][individual_stat] = 0
                                        continue

                                pokemon_potential = round((total_IV / 45.0), 2)
                                pokemon_num = int(pokemon['pokemon_data'][
                                                  'pokemon_id']) - 1
                                pokemon_name = self.pokemon_list[
                                    int(pokemon_num)]['Name']
                                logger.log('[#] A Wild {} appeared! [CP {}] [Potential {}]'.format(
                                    pokemon_name, cp, pokemon_potential), 'yellow')

                                logger.log('[#] IV [Stamina/Attack/Defense] = [{}/{}/{}]'.format(
                                    pokemon['pokemon_data']['individual_stamina'],
                                    pokemon['pokemon_data']['individual_attack'],
                                    pokemon['pokemon_data']['individual_defense']
                                ))
                                pokemon['pokemon_data']['name'] = pokemon_name
                                # Simulate app
                                sleep(3)

                        balls_stock = self.bot.pokeball_inventory()
                        while(True):

                            pokeball = 1 # default:poke ball

                            if balls_stock[1] <= 0: # if poke ball are out of stock
                                if balls_stock[2] > 0: # and player has great balls in stock...
                                    pokeball = 2 # then use great balls
                                elif balls_stock[3] > 0: # or if great balls are out of stock too, and player has ultra balls...
                                    pokeball = 3 # then use ultra balls
                                else:
                                    pokeball = 0 # player doesn't have any of pokeballs, great balls or ultra balls

                            while(pokeball < 3):
                                if catch_rate[pokeball-1] < 0.35 and balls_stock[pokeball+1] > 0:
                                    # if current ball chance to catch is under 35%, and player has better ball - then use it
                                    pokeball = pokeball+1 # use better ball
                                else:
                                    break

                            # @TODO, use the best ball in stock to catch VIP (Very Important Pokemon: Configurable)

                            if pokeball is 0:
                                logger.log(
                                    '[x] Out of pokeballs, switching to farming mode...', 'red')
                                # Begin searching for pokestops.
                                self.config.mode = 'farm'
                                return PokemonCatchWorker.NO_POKEBALLS

                            balls_stock[pokeball] = balls_stock[pokeball] - 1
                            success_percentage = '{0:.2f}'.format(catch_rate[pokeball-1]*100)
                            logger.log('[x] Using {} (chance: {}%)... ({} left!)'.format(
                                self.item_list[str(pokeball)], 
                                success_percentage, 
                                balls_stock[pokeball]
                            ))

                            id_list1 = self.count_pokemon_inventory()
                            self.api.catch_pokemon(encounter_id=encounter_id,
                                                   pokeball=pokeball,
                                                   normalized_reticle_size=1.950,
                                                   spawn_point_guid=spawnpoint_id,
                                                   hit_pokemon=1,
                                                   spin_modifier=1,
                                                   NormalizedHitPosition=1)
                            response_dict = self.api.call()

                            if response_dict and \
                                'responses' in response_dict and \
                                'CATCH_POKEMON' in response_dict['responses'] and \
                                    'status' in response_dict['responses']['CATCH_POKEMON']:
                                status = response_dict['responses'][
                                    'CATCH_POKEMON']['status']
                                if status is 2:
                                    logger.log(
                                        '[-] Attempted to capture {}- failed.. trying again!'.format(pokemon_name), 'red')
                                    sleep(2)
                                    continue
                                if status is 3:
                                    logger.log(
                                        '[x] Oh no! {} vanished! :('.format(pokemon_name), 'red')
                                if status is 1:
                                    logger.log(
                                        '[x] Captured {}! [CP {}] [IV {}]'.format(
                                            pokemon_name,
                                            cp,
                                            pokemon_potential
                                        ), 'green'
                                    )

                                    id_list2 = self.count_pokemon_inventory()

                                    self.release_or_evolve(
                                        pokemon_id=list(Set(id_list2) - Set(id_list1))[0],
                                        cp=cp,
                                        pokemon_name=pokemon_name,
                                    )

                                    # if self.config.evolve_captured:
                                    #     pokemon_to_transfer = list(Set(id_list2) - Set(id_list1))
                                    #     self.api.evolve_pokemon(pokemon_id=pokemon_to_transfer[0])
                                    #     response_dict = self.api.call()
                                    #     status = response_dict['responses']['EVOLVE_POKEMON']['result']
                                    #     if status == 1:
                                    #         logger.log(
                                    #                 '[#] {} has been evolved!'.format(pokemon_name), 'green')
                                    #     else:
                                    #         logger.log(
                                    #         '[x] Failed to evolve {}!'.format(pokemon_name))
                                    #
                                    # if self.should_release_pokemon(pokemon_name, cp, pokemon_potential, response_dict):
                                    #     # Transfering Pokemon
                                    #     pokemon_to_transfer = list(
                                    #         Set(id_list2) - Set(id_list1))
                                    #     if len(pokemon_to_transfer) == 0:
                                    #         raise RuntimeError(
                                    #             'Trying to transfer 0 pokemons!')
                                    #     self.transfer_pokemon(
                                    #         pokemon_to_transfer[0])
                                    #     logger.log(
                                    #         '[#] {} has been exchanged for candy!'.format(pokemon_name), 'green')
                                    logger.log(
                                        '[x] Captured {}! [CP {}]'.format(pokemon_name, cp), 'green')
                            break
        time.sleep(5)

    def get_my_pokemon(self, inventory_response):
        items = inventory_response['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        my_pokemon_list = []
        for item in items:
            if 'pokemon_data' in item['inventory_item_data']:
                my_pokemon_list.append(item['inventory_item_data']['pokemon_data'])

        pokemon_by_species = defaultdict(list)
        for pokemon in my_pokemon_list:
            if 'pokemon_id' in pokemon:
                # not an egg
                pokemon_by_species[pokemon['pokemon_id']].append(pokemon)

        pokemon_by_species2 = {}
        for species, pokemons in pokemon_by_species.items():
            pokemon_by_species2[species] = sorted(
                pokemons, key=operator.itemgetter('cp'), reverse=True,
            )

        return pokemon_by_species2

    def get_candies(self, inventory_response):
        items = inventory_response['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']
        candy_by_family = {}
        for item in items:
            if 'pokemon_family' in item['inventory_item_data']:
                item2 = item['inventory_item_data']['pokemon_family']
                candy_by_family[item2['family_id']] = item2['candy']

        return candy_by_family

    def release_or_evolve(self, pokemon_id, pokemon_name, cp):
        pokemon_name = pokemon_name.lower()

        self.api.get_inventory()
        response = self.api.call()

        candy_by_family = self.get_candies(response)
        my_pokemon = self.get_my_pokemon(response)

        candies_needed_for_evolve = candies_to_evolve.get(pokemon_name)
        if not candies_needed_for_evolve:
            print 'NO CANDY INFORMATION FOUND FOR {}'.format(pokemon_name)
            return
        family_id = pokemon_name_to_family_id.get(pokemon_name)
        if not family_id:
            print 'NO FAMILY FOUND FOR {}'.format(pokemon_name)
            return
        candies_available = candy_by_family.get(family_id)

        pokemons_in_species = my_pokemon.get(family_id)

        if candies_available is None:
            amount_of_upgrades = 0
        else:
            amount_of_upgrades = int(candies_available / candies_needed_for_evolve)

        iteration = 0
        for pokemon in pokemons_in_species:
            pokemon_id = pokemon['id']

            if iteration < amount_of_upgrades:
                print '  evolving {}'.format(pokemon_id)
                self.api.evolve_pokemon(pokemon_id=pokemon_id)
                self.api.call()
                sleep(20)
            elif iteration == amount_of_upgrades:
                print '  keeping {}'.format(pokemon_id)
            else:
                print '  releasing {}'.format(pokemon_id)
                self.api.release_pokemon(pokemon_id=pokemon_id)
                self.api.call()
                sleep(1)
            iteration += 1

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


    def _transfer_low_cp_pokemon(self, value):
        self.api.get_inventory()
        response_dict = self.api.call()
        self._transfer_all_low_cp_pokemon(value, response_dict)

    def _transfer_all_low_cp_pokemon(self, value, response_dict):
        try:
            reduce(dict.__getitem__, [
                   "responses", "GET_INVENTORY", "inventory_delta", "inventory_items"], response_dict)
        except KeyError:
            pass
        else:
            for item in response_dict['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']:
                try:
                    reduce(dict.__getitem__, [
                           "inventory_item_data", "pokemon"], item)
                except KeyError:
                    pass
                else:
                    pokemon = item['inventory_item_data']['pokemon']
                    self._execute_pokemon_transfer(value, pokemon)
                    time.sleep(1.2)

    def _execute_pokemon_transfer(self, value, pokemon):
        if 'cp' in pokemon and pokemon['cp'] < value:
            self.api.release_pokemon(pokemon_id=pokemon['id'])
            response_dict = self.api.call()

    def transfer_pokemon(self, pid):
        self.api.release_pokemon(pokemon_id=pid)
        response_dict = self.api.call()

    def count_pokemon_inventory(self):
        self.api.get_inventory()
        response_dict = self.api.call()
        id_list = []
        return self.counting_pokemon(response_dict, id_list)

    def counting_pokemon(self, response_dict, id_list):
        try:
            reduce(dict.__getitem__, [
                   "responses", "GET_INVENTORY", "inventory_delta", "inventory_items"], response_dict)
        except KeyError:
            pass
        else:
            for item in response_dict['responses']['GET_INVENTORY']['inventory_delta']['inventory_items']:
                try:
                    reduce(dict.__getitem__, [
                           "inventory_item_data", "pokemon_data"], item)
                except KeyError:
                    pass
                else:
                    pokemon = item['inventory_item_data']['pokemon_data']
                    if pokemon.get('is_egg', False):
                        continue
                    id_list.append(pokemon['id'])

        return id_list

    def should_release_pokemon(self, pokemon_name, cp, iv, response_dict):
        if self._check_always_capture_exception_for(pokemon_name):
            return False
        else:
            release_config = self._get_release_config_for(pokemon_name)
            cp_iv_logic = release_config.get('cp_iv_logic')
            if not cp_iv_logic:
                cp_iv_logic = self._get_release_config_for('any').get('cp_iv_logic', 'and')

            release_results = {
                'cp':               False,
                'iv':               False,
            }

            if 'release_under_cp' in release_config:
                min_cp = release_config['release_under_cp']
                if cp < min_cp:
                    release_results['cp'] = True

            if 'release_under_iv' in release_config:
                min_iv = release_config['release_under_iv']
                if iv < min_iv:
                    release_results['iv'] = True

            if release_config.get('always_release'):
                return True

            logic_to_function = {
                'or': lambda x, y: x or y,
                'and': lambda x, y: x and y
            }

            #logger.log(
            #    "[x] Release config for {}: CP {} {} IV {}".format(
            #        pokemon_name,
            #        min_cp,
            #        cp_iv_logic,
            #        min_iv
            #    ), 'yellow'
            #)

            return logic_to_function[cp_iv_logic](*release_results.values())

    def _get_release_config_for(self, pokemon):
        release_config = self.config.release_config.get(pokemon)
        if not release_config:
            release_config = self.config.release_config['any']
        return release_config

    def _get_exceptions(self):
        exceptions = self.config.release_config.get('exceptions')
        if not exceptions:
            return None
        return exceptions

    def _get_always_capture_list(self):
        exceptions = self._get_exceptions()
        if not exceptions:
            return []
        always_capture_list = exceptions['always_capture']
        if not always_capture_list:
            return []
        return always_capture_list

    def _check_always_capture_exception_for(self, pokemon_name):
        always_capture_list = self._get_always_capture_list()
        if not always_capture_list:
            return False
        else:
            for pokemon in always_capture_list:
                if pokemon_name == str(pokemon):
                    return True
        return False
