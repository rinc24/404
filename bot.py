# !/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from config import token, proxy, path_db, path_log, name_bot
from constant_dict import *
from datetime import datetime
import json
from telebot import types
from random import shuffle
from os.path import exists


bot = telebot.TeleBot(token)
telebot.apihelper.proxy = {'https': proxy}


def convert_time(time_unix):
    return datetime.utcfromtimestamp(time_unix + 18000).strftime('%d.%m.%Y %H:%M:%S')


with open(f"{path_db}default_user.json") as file:
    default_user = json.load(file)

with open(f"{path_db}default_chat.json") as file:
    default_chat = json.load(file)


def logger(chat_id, text, user_name=""):
    with open(f"{path_log}{chat_id}", "a") as log:
        log.write(datetime.now().strftime("%d.%m.%Y %H:%M:%S ") + user_name + ": " + text + "\n")


class User:
    """Создан специально для игры 404"""
    def __init__(self, user):
        for key in default_user.keys():
            if key not in user.keys():
                user[key] = default_user[key]
        for key in user.keys():
            if key not in default_user.keys():
                user.pop(key)
        self.rating = user["rating"]
        self.want_fold = user["want_fold"]
        self.hand = user["hand"]
        self.move_card_count = user["move_card_count"]
        self.take_card_count = user["take_card_count"]
        self.id = user["id"]
        self.is_bot = user["is_bot"]
        self.first_name = user["first_name"]
        self.username = user["username"]
        self.last_name = user["last_name"]
        self.language_code = user["language_code"]

    def dict(self):
        return {
            "rating": self.rating,
            "want_fold": self.want_fold,
            "hand": self.hand,
            "move_card_count": self.move_card_count,
            "take_card_count": self.take_card_count,
            "id": self.id,
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "username": self.username,
            "last_name": self.last_name,
            "language_code": self.language_code
        }

    def update_user(self, user):
        self.id = user["id"]
        self.is_bot = user["is_bot"]
        self.first_name = user["first_name"]
        self.username = user["username"]
        self.last_name = user["last_name"]
        self.language_code = user["language_code"]


class Game:
    """Создан специально для игры 404"""
    def __init__(self, message: types.Message, from_user=None):
        if from_user is None:
            from_user = message.from_user
        self.chat_id = message.chat.id
        self.user_id = from_user.id
        self.message_id = message.message_id
        self.text = message.text
        if not exists(f"{path_db}{self.chat_id}.json"):
            chat = default_chat
        else:
            with open(f"{path_db}{self.chat_id}.json") as db:
                chat = json.load(db)
        for key in default_chat.keys():
            if key not in chat.keys():
                chat[key] = default_chat[key]
        for key in chat.keys():
            if key not in default_chat.keys():
                chat.pop(key)
        self.in_game = chat["in_game"]
        self.type_game = chat["type_game"]
        self.cards_sticky = chat["cards_sticky"]
        self.deck_skin = chat["deck_skin"]
        self.cards_to_hand = chat["cards_to_hand"]
        self.number_of_decks = chat["number_of_decks"]
        self.move = chat["move"]
        self.who_move = chat["who_move"]
        self.who_will_move = chat["who_will_move"]
        self.messages_to_delete = chat["messages_to_delete"]
        self.used = chat["used"]
        self.not_used = chat["not_used"]
        self.games_count = chat["games_count"]
        self.players = chat["players"]
        self.winners = chat["winners"]
        self.want_new_game = chat["want_new_game"]
        self.chosen_suit = chat["chosen_suit"]
        self.users = {user: User(chat["users"][user]) for user in chat["users"]}
        if str(self.user_id) not in self.users:
            with open(f"{path_db}default_user.json") as db:
                self.users.update({str(self.user_id): User(json.load(db))})
        self.users[str(self.user_id)].update_user(from_user.__dict__)

    def dump(self):
        chat = {
            "chat_id": self.chat_id,
            "in_game": self.in_game,
            "type_game": self.type_game,
            "cards_sticky": self.cards_sticky,
            "deck_skin": self.deck_skin,
            "cards_to_hand": self.cards_to_hand,
            "number_of_decks": self.number_of_decks,
            "move": self.move,
            "who_move": self.who_move,
            "who_will_move": self.who_will_move,
            "messages_to_delete": self.messages_to_delete,
            "used": self.used,
            "not_used": self.not_used,
            "games_count": self.games_count,
            "players": self.players,
            "winners": self.winners,
            "want_new_game": self.want_new_game,
            "chosen_suit": self.chosen_suit,
            "users": {}
        }
        for user_id in self.users:
            chat["users"].update({user_id: self.users[user_id].dict()})
        with open(f"{path_db}{self.chat_id}.json", "w+") as db:
            json.dump(chat, db, indent=4)

    def can_move(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        if self.who_move == user_id:
            return True
        else:
            return False

    def next_move(self):
        self.users[str(self.who_move)].move_card_count = 0
        self.users[str(self.who_move)].take_card_count = 0
        self.users[str(self.who_move)].want_fold = 0
        self.move += 1
        # if self.who_move == self.who_will_move:
        #     self.who_will_move = self.next_player(self.who_move)
        self.who_move = self.who_will_move

    def new_game(self):
        self.in_game = False
        self.move = 0
        self.who_move = 0
        self.who_will_move = 0
        self.used = []
        self.not_used = []
        self.players = []
        self.winners = []
        self.want_new_game = []
        self.chosen_suit = ""
        for user_id in self.users.keys():
            self.users[user_id].hand = []
            self.users[user_id].move_card_count = 0
            self.users[user_id].take_card_count = 0
            self.users[user_id].want_fold = False
        self.delete_bot_messages()

    def go(self):
        if self.user_id not in self.players:
            self.players.append(self.user_id)

    def pass_game(self):
        if self.user_id in self.players:
            self.players.remove(self.user_id)

    def start_game(self):
        if self.type_game == "404":
            self.not_used = [_ for _ in deck54 * self.number_of_decks]
        else:
            self.not_used = [_ for _ in deck36]
        shuffle(self.not_used)
        self.in_game = True
        self.move = 1
        self.who_move = self.players[0]
        self.who_will_move = self.players[0]
        for user_id in self.players:
            for _ in range(self.cards_to_hand):
                self.users[str(user_id)].hand.append(self.not_used.pop())
            self.users[str(user_id)].hand.sort()
        self.used.append(self.users[str(self.who_move)].hand.pop())
        self.users[str(self.who_move)].move_card_count += 1

    def fold(self):
        for card in self.users[str(self.user_id)].hand:
            self.not_used.append(card)
        shuffle(self.not_used)
        self.users[str(self.user_id)].hand = []
        if self.can_move(self.user_id):
            self.next_move()
        self.players.remove(self.user_id)
        self.users[str(self.user_id)].want_fold = False
        self.users[str(self.user_id)].move_card_count = 0
        self.users[str(self.user_id)].take_card_count = 0

    def used_to_not_used(self):
        self.not_used = [i for i in self.used]
        new_used = [self.used[-1]]
        while self.used[-1][0] == "J":
            self.used.pop()
            new_used.append(self.used.pop())
        self.used = new_used
        self.used.reverse()
        shuffle(self.not_used)
        bot.send_message(self.chat_id, "<b><i>Перемешали колоду.</i></b>", disable_notification=True, parse_mode="HTML")

    def take_card(self):
        if len(self.not_used) != 0:
            self.users[str(self.user_id)].hand.append(self.not_used.pop())
        elif len(self.used) > 1:
            self.used_to_not_used()
            self.users[str(self.user_id)].hand.append(self.not_used.pop())
        self.users[str(self.user_id)].take_card_count += 1

    def get_penalty_cards(self, user_id, amount):
        count = 0
        if user_id is None:
            user_id = self.user_id
        for _ in range(amount):
            if len(self.not_used) != 0:
                self.users[str(user_id)].hand.append(self.not_used.pop())
                count += 1
            elif len(self.used) > 1:
                self.used_to_not_used()
                self.users[str(user_id)].hand.append(self.not_used.pop())
                count += 1
            else:
                return count
        return count

    def get_last_card(self):
        if len(self.used) != 0:
            return self.used[-1]
        else:
            return "card"

    def get_hand(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        return self.users[str(user_id)].hand

    def get_rating(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        return self.users[str(user_id)].rating

    def get_take_card_count(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        return self.users[str(user_id)].take_card_count

    def get_move_card_count(self, user_id=None):
        if user_id is None:
            user_id = self.who_move
        return self.users[str(user_id)].move_card_count

    def get_first_name(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        first_name = self.users[str(user_id)].first_name
        if first_name is not None:
            return first_name + " "
        else:
            return ""

    def get_last_name(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        last_name = self.users[str(user_id)].last_name
        if last_name is not None:
            return last_name + " "
        else:
            return ""

    def get_username(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        username = self.users[str(user_id)].username
        if username is not None:
            return str("@" + username + " ")
        else:
            return ""

    def get_player_full_name(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        self.users[str(user_id)].rating = round(self.users[str(user_id)].rating, 2)
        first_name = self.get_first_name(user_id)
        last_name = self.get_last_name(user_id)
        username = self.get_username(user_id)
        rating = self.get_rating(user_id)
        return f"{first_name}{last_name}{username}R:{rating}"

    def get_player_short_name(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        return self.get_player_full_name(user_id).split()[0]

    def add_players_list(self):
        players_list = ""
        for user_id in self.players:
            index = self.players.index(user_id) + 1
            player_full_name = self.get_player_full_name(user_id)
            string = f"{index}. {player_full_name}"
            if user_id == self.who_move:
                string = f"<b>" + string + f"</b>\n"
            else:
                string += "\n"
            players_list += string
        return players_list

    def add_users_list(self):
        users_list = ""
        for user_id in self.users.keys():
            player_full_name = self.get_player_full_name(user_id)
            string = f"{player_full_name}\n"
            users_list += string
        return users_list

    def pre_joker_card(self):
        joker_card = "card"
        for card in self.used[::-1]:
            if card[0] == "J":
                joker_card = card
            elif joker_card[0] == "J" and card[0] != "J":
                return card
        return joker_card

    def pre_used_card(self, card):
        return self.used[(len(self.used)) - self.used[::-1].index(card) - 2]

    def is_it_relevant(self):
        last_card = self.get_last_card()
        new_card = self.text
        last_card_rank = last_card[0]
        if last_card_rank == "Д":
            last_card_suit = self.chosen_suit
        else:
            last_card_suit = last_card[-2:4]
        new_card_rank = new_card[0]
        new_card_suit = new_card[-2:4]
        ranks = [last_card_rank, new_card_rank]
        if "J" in ranks and ((last_card_suit in black_suits and new_card_suit in black_suits) or
                             (last_card_suit in red_suits and new_card_suit in red_suits)):
            return True
        elif new_card_rank == "Д":
            return True
        elif last_card_suit == new_card_suit or last_card_rank == new_card_rank:
            return True
        elif last_card_rank == "J":
            last_card_rank = self.pre_joker_card()[0]
            if last_card_rank == new_card_rank:
                return True
            elif last_card_rank == "Д" and new_card_suit == self.chosen_suit:
                return True
        return False

    def is_it_sticky(self):
        last_card = self.get_last_card()
        new_card = self.text
        last_card_rank = last_card[0]
        last_card_suit = last_card[-2:4]
        new_card_rank = new_card[0]
        new_card_suit = new_card[-2:4]
        if last_card_rank != "J":
            if last_card_rank == new_card_rank:
                return True and self.cards_sticky
            elif last_card_rank in ["2", "6"] and (last_card_suit == new_card_suit or new_card_rank == "Д"):
                return True
            elif new_card_rank == "J" and ((last_card_suit in black_suits and new_card_suit in black_suits) or
                                           (last_card_suit in red_suits and new_card_suit in red_suits)):
                return True and (self.cards_sticky or last_card_rank in ["2", "6"])
        else:
            if last_card_rank == new_card_rank:
                return True
            last_card_rank = self.pre_joker_card()[0]
            if last_card_rank == new_card_rank:
                return True and self.cards_sticky
            elif last_card_rank in ["2", "6"] and ((last_card_suit in black_suits and new_card_suit in black_suits) or
                                                   (last_card_suit in red_suits and new_card_suit in red_suits) or
                                                   new_card_rank == "Д" or new_card_rank == last_card_rank):
                return True
        return False

    def is_it_ok_card(self):
        if self.get_move_card_count() == 0 or self.who_move == self.who_will_move:
            return self.is_it_relevant()
        else:
            return self.is_it_sticky()

    def am_i_admin(self):
        for i in bot.get_chat_administrators(self.chat_id):
            if i.user.username == name_bot:
                return True
        return False

    def can_take(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        if self.get_last_card()[0] in ("2", "6"):
            return True
        elif self.get_last_card()[0] == "J" and self.pre_joker_card()[0] in ("2", "6"):
            return True
        elif self.get_take_card_count(user_id) == 0 and self.get_move_card_count(user_id) == 0:
            return True
        return False

    def can_end_move(self):
        if self.get_move_card_count() != 0:
            if self.get_last_card()[0] == "J":
                last_card = self.pre_joker_card()
            else:
                last_card = self.get_last_card()
            if last_card[0] not in ["2", "6"]:
                return True
        elif self.get_take_card_count() != 0:
            return True
        return False

    def next_player(self, player_id):
        if player_id == self.players[-1]:
            return self.players[0]
        else:
            return self.players[self.players.index(player_id) + 1]

    def next_next_player(self, player_id):
        player_id = self.next_player(player_id)
        return self.next_player(player_id)

    def end_move(self, chosen_suit=""):
        self.next_move()
        self.delete_bot_messages()
        self.chosen_suit = chosen_suit
        bot.delete_message(self.chat_id, self.message_id)
        if self.get_last_card()[0] == "9" and len(self.users[str(self.user_id)].hand) == 0:
            self.new_winner()
        elif self.get_last_card()[0] == "J":
            if self.pre_joker_card()[0] == "9" and len(self.users[str(self.user_id)].hand) == 0:
                self.new_winner()
        if len(self.players) == 1:
            self.end_of_game()
            return None
        markup = self.gen_keyboard_in_game_selective()
        mention = self.gen_mention(self.who_move)
        bot.send_message(self.chat_id, f"<b>Ход {self.move}.</b>\n{mention}:",
                         reply_markup=markup, parse_mode="HTML", disable_notification=True)

    def gen_keyboard_in_game_selective(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=6, selective=True)
        user_id = self.who_move
        hand = self.users[str(user_id)].hand
        hand.sort()
        markup.add(*hand)
        keyboard = [[key for key in row] for row in keyboard_in_game]
        if not self.can_end_move():
            keyboard[0].remove("Конец хода")
        if not self.can_take(user_id):
            keyboard[0].remove("Беру")
        if user_id in self.want_new_game:
            keyboard[1].remove("Новая игра")
        for row in keyboard:
            markup.row(*row)
        return markup

    def gen_keyboard_choice_suit(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        user_id = self.who_move
        keyboard = [card_suits, [key for key in keyboard_in_game[0]], [key for key in keyboard_in_game[1]]]
        keyboard[1].remove("Конец хода")
        if not self.can_take(user_id):
            keyboard[1].remove("Беру")
        if user_id in self.want_new_game:
            keyboard[2].remove("Новая игра")
        for row in keyboard:
            markup.row(*row)
        return markup

    def gen_mention(self, user_id=None):
        if user_id is None:
            user_id = self.user_id
        name = self.get_player_short_name(user_id)
        return f'<a href="tg://user?id={user_id}">{name}</a>'

    def delete_bot_messages(self):
        for message_id in self.messages_to_delete:
            try:
                bot.delete_message(self.chat_id, message_id)
            except telebot.apihelper.ApiException:
                pass
        self.messages_to_delete = []

    def penalty(self, card):
        if card[0] == "J":
            card = self.pre_joker_card()
        card_rank = card[0]
        next_player = self.next_player(self.who_will_move)
        next_next_player = self.next_next_player(self.who_will_move)
        if ((self.type_game == "404" and card in penalty_dict_404) or
           (self.type_game == "101" and card in penalty_dict_101)):
            if self.type_game == "404":
                penalty_dict = penalty_dict_404
            else:
                penalty_dict = penalty_dict_101
            if card_rank == self.pre_used_card(card)[0] and self.pre_used_card(card) not in penalty_dict and\
                    self.get_move_card_count() > 0:
                cards_amount = self.get_penalty_cards(self.who_will_move, penalty_dict[card])
                self.who_will_move = next_player
                mention = self.gen_mention(self.who_will_move)
            else:
                cards_amount = self.get_penalty_cards(next_player, penalty_dict[card])
                self.who_will_move = next_next_player
                mention = self.gen_mention(next_player)
            bot.send_message(self.chat_id, f"<i>{mention} {how_many_cards(cards_amount)}</i>",
                             disable_notification=True, parse_mode="HTML")
        elif (card_rank in ["3", "5", "1", "Д", "1", "9", "В", "К"] and
              (self.get_move_card_count() == 1 or card_rank != self.pre_used_card(card)[0])):
            self.who_will_move = next_player
        elif card_rank in ["2", "6"]:
            pass

    def add_winners_list(self):
        winners_list = ""
        for user_id in self.winners:
            index = self.winners.index(user_id) + 1
            player_full_name = self.get_player_full_name(user_id)
            if index == 1:
                winners_list += f"{index}. {player_full_name}+1.00\n"
                self.users[str(user_id)].rating += 1.00
            elif index == 2:
                winners_list += f"{index}. {player_full_name}+0.10\n"
                self.users[str(user_id)].rating += 0.10
            elif index == 3:
                winners_list += f"{index}. {player_full_name}+0.01\n"
                self.users[str(user_id)].rating += 0.01
            else:
                winners_list += f"{index}. {player_full_name}\n"
        return winners_list

    def end_of_game(self):
        self.winners.append(self.players.pop())
        answer = f"Игра закончилась {how_many_move(self.move - 1)}\n"
        answer += self.add_winners_list()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("Новая игра")
        bot.send_message(self.chat_id, answer, reply_markup=markup)
        self.in_game = False
        self.move = 0
        self.who_move = 0
        self.messages_to_delete = []
        self.used = []
        self.not_used = []
        self.games_count += 1
        self.players = []
        self.winners = []
        self.want_new_game = []
        self.chosen_suit = ""

    def new_winner(self):
        self.winners.append(self.user_id)
        self.players.remove(self.user_id)
        bot.send_message(self.chat_id,
                         f"<i><b>{self.get_player_short_name()} выходит "
                         f"заняв {self.winners.index(self.user_id) + 1}-ю позицию.</b></i>",
                         parse_mode="HTML", disable_notification=True)
        self.users[str(self.user_id)].hand = []
        self.users[str(self.user_id)].take_card_count = 0
        self.users[str(self.user_id)].want_fold = False

    def rating(self):
        pass


def how_many_cards(num):
    if num == 0:
        return "пропускает ход."
    elif num == 1:
        return "берет одну карту."
    elif num % 10 in [0, 5, 6, 7, 8, 9] or num in [11, 12, 13, 14]:
        return f"берет {num} карт."
    elif num % 10 in [2, 3, 4]:
        return f"берет {num} карты."


def how_many_move(num):
    if num == 0:
        return "без единого хода."
    elif num == 1:
        return "на первом ходу."
    elif num == 3:
        return f"на {num}-ем ходу."
    else:
        return f"на {num}-ом ходу."


def gen_keyboard_in_game_for_any():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(*keyboard_in_game[1])
    return markup


def gen_keyboard_new_game():
    markup = types.InlineKeyboardMarkup()
    keyboard = keyboard_new_game
    for row in keyboard:
        buttons = [types.InlineKeyboardButton(text=KEY, callback_data=row[KEY]) for KEY in row]
        markup.row(*buttons)
    return markup


def is_it_card(card):
    if type(card) == str and card in deck54:
        return True
    else:
        return False


def am_i_admin(message):
    for i in bot.get_chat_administrators(message.chat.id):
        if i.user.username == name_bot:
            return True
    return False


# КОЛБЕКИ НОВОЙ ИГРЫ:


@bot.callback_query_handler(func=lambda call: True if call.data == "/start_game" else False)
def cmd_start_game(call: types.CallbackQuery):
    game = Game(call.message, from_user=call.from_user)
    if not game.in_game and len(game.players) in players_range:
        game.start_game()
        player_short_name = game.get_player_short_name(game.who_move)
        answer = f"Игра №{game.games_count + 1} началась!\n\n<b>Ход 1.</b>\nПервым ходит {player_short_name}:"
        bot.edit_message_text(answer, game.chat_id, game.message_id, parse_mode="HTML")
        markup = gen_keyboard_in_game_for_any()
        bot.send_sticker(game.chat_id, skins[game.deck_skin][game.get_last_card()],
                         reply_markup=markup, disable_notification=True)
        game.penalty(game.get_last_card())
        mention = game.gen_mention(game.who_move)
        if game.get_last_card()[0] not in ["2", "6"]:
            answer = f"{mention}, есть что добавить?"
        else:
            answer = f"{mention}, придется крыть."
        markup = game.gen_keyboard_in_game_selective()
        msg = bot.send_message(game.chat_id, answer, reply_markup=markup,
                               parse_mode="HTML", disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
        game.dump()


@bot.callback_query_handler(func=lambda call: True if call.data == "/go" else False)
def cmd_go(call: types.CallbackQuery):
    game = Game(call.message, from_user=call.from_user)
    if not game.in_game and game.user_id not in game.players:
        game.players.append(game.user_id)
        markup = gen_keyboard_new_game()
        answer = "Начинаем новую игру! Вступай!\nОт 2-ух до 8-ми игроков.\nПравила игры: /help\n\nСписок:\n"
        answer += game.add_players_list()
        bot.edit_message_text(answer, game.chat_id, game.message_id, reply_markup=markup)
    game.dump()


@bot.callback_query_handler(func=lambda call: True if call.data == "/pass" else False)
def cmd_pass(call: types.CallbackQuery):
    game = Game(call.message, from_user=call.from_user)
    if not game.in_game and game.user_id in game.players:
        game.players.remove(game.user_id)
        game.dump()
        markup = gen_keyboard_new_game()
        answer = f"Начинаем новую игру! Вступай!\nОт 2-ух до 8-ми игроков.\nПравила игры: /help\n\nСписок:\n"
        answer += game.add_players_list()
        bot.edit_message_text(answer, game.chat_id, game.message_id, reply_markup=markup)


# ОБРАБОТКА КНОПОК:


@bot.message_handler(content_types=['text'], func=lambda message: is_it_card(message.text)
                     and message.chat.type in ["group", "supergroup"])
def cmd_card(message: types.Message):
    game = Game(message)
    card = game.text
    if game.in_game and game.can_move() and card in game.get_hand():
        if game.is_it_ok_card():
            game.used.append(card)
            game.users[str(game.user_id)].hand.remove(card)
            game.users[str(game.user_id)].move_card_count += 1
            markup = game.gen_keyboard_in_game_selective()
            bot.send_sticker(game.chat_id, skins[game.deck_skin][card], reply_markup=markup,
                             reply_to_message_id=game.message_id, disable_notification=True)
            game.penalty(card)
            game.dump()
    bot.delete_message(game.chat_id, game.message_id)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == "Конец хода"
                     and message.chat.type in ["group", "supergroup"])
def cmd_end_move(message: types.Message):
    game = Game(message)
    if game.can_move() and game.in_game:
        if game.get_move_card_count() == 0:
            if game.get_take_card_count() == 0:
                markup = game.gen_keyboard_in_game_selective()
                bot.delete_message(game.chat_id, game.message_id)
                mention = game.gen_mention(game.user_id)
                msg = bot.send_message(game.chat_id, f"<i>{mention}, возьми карту из колоды!</i>",
                                       reply_markup=markup, disable_notification=True, parse_mode="HTML")
                game.messages_to_delete.append(msg.message_id)
                game.dump()
            else:
                bot.send_message(game.chat_id, f"<i>{game.get_player_short_name()}"
                                               f" взял карту и не нашел чем сходить.</i>",
                                 disable_notification=True, parse_mode="HTML")
                game.who_will_move = game.next_player(game.who_move)
                game.end_move(game.chosen_suit)
                game.dump()
        else:
            if game.get_last_card()[0] == "J":
                last_card = game.pre_joker_card()
            else:
                last_card = game.get_last_card()

            if last_card[0] in ["2", "6"]:
                markup = game.gen_keyboard_in_game_selective()
                bot.delete_message(game.chat_id, game.message_id)
                player_short_name = game.get_player_short_name(game.user_id)
                msg = bot.send_message(game.chat_id, f"<i>{player_short_name}, надо крыть!</i>",
                                       reply_markup=markup, disable_notification=True, parse_mode="HTML")
                game.messages_to_delete.append(msg.message_id)
                game.dump()
            elif last_card[0] == "Д":
                markup = game.gen_keyboard_choice_suit()
                mention = game.gen_mention(game.user_id)
                bot.delete_message(game.chat_id, game.message_id)
                msg = bot.send_message(game.chat_id, f"<i>{mention}, выбери масть.</i>",
                                       reply_markup=markup, disable_notification=True, parse_mode="HTML")
                game.messages_to_delete.append(msg.message_id)
                game.dump()
            else:
                game.end_move()
                game.dump()
    else:
        bot.delete_message(game.chat_id, game.message_id)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == "Беру"
                     and message.chat.type in ["group", "supergroup"])
def cmd_take_card(message: types.Message):
    game = Game(message)
    if game.can_move(game.user_id) and game.in_game and game.can_take(game.user_id):
        game.take_card()
        markup = game.gen_keyboard_in_game_selective()
        mention = game.gen_mention(game.user_id)
        bot.delete_message(game.chat_id, game.message_id)
        msg = bot.send_message(game.chat_id, f"<i>{mention} берет карту.</i>",
                               parse_mode="HTML", reply_markup=markup, disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
        game.dump()
    else:
        bot.delete_message(game.chat_id, game.message_id)


@bot.message_handler(content_types=['text'], func=lambda message:
                     message.text in ["/new_game", "Новая игра", "/new_game@game404bot", "/start", "/start@game404bot"]
                     and message.chat.type in ["group", "supergroup"])
def cmd_new_game(message: types.Message):
    game = Game(message)
    if game.in_game and game.user_id in game.want_new_game:
        msg = bot.send_message(game.chat_id, "Новая игра начнется если этого захочет кто-то еще.",
                               disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
        markup = game.gen_keyboard_in_game_selective()
        mention = game.gen_mention(game.who_move)
        msg = bot.send_message(game.chat_id, f"Новая игра еще не началась. \n"
                                             f"{mention}, продолжай ход.",
                               reply_markup=markup, parse_mode="HTML", disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
    elif game.in_game and len(game.want_new_game) == 0:
        game.want_new_game.append(game.user_id)
        msg = bot.send_message(game.chat_id, 'Запрос на новую игру принят. \nКто-то еще согласен?\n'
                                             'Жми "Новая игра" или команду /new_game.', disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
        mention = game.gen_mention(game.who_move)
        markup = game.gen_keyboard_in_game_selective()
        msg = bot.send_message(game.chat_id, f"Новая игра еще не началась. \n"
                                             f"{mention}, продолжай ход.",
                               reply_markup=markup, parse_mode="HTML", disable_notification=True)
        game.messages_to_delete.append(msg.message_id)
    else:
        markup = types.ReplyKeyboardRemove()
        msg = bot.send_message(game.chat_id, "<i>Удаление прошлой игры...</i>",
                               reply_markup=markup, disable_notification=True, parse_mode="HTML")
        game.messages_to_delete.append(msg.message_id)
        game.new_game()
        game.players.append(game.user_id)
        markup = gen_keyboard_new_game()
        answer = f"Начинаем новую игру! Вступай!\n" \
                 f"От 2-ух до 8-ми игроков.\n" \
                 f"Правила игры: /help\n\n" \
                 f"Список:\n"
        answer += game.add_players_list()
        bot.send_message(game.chat_id, answer, reply_markup=markup)
    game.dump()


@bot.message_handler(content_types=['text'], func=lambda message: True
                     if message.text in ["/fold", "Сдаюсь", "/fold@game404bot"] else False)
def cmd_fold(message: types.Message):
    game = Game(message)
    if game.in_game and game.user_id in game.players:
        if game.users[str(game.user_id)].want_fold:
            game.fold()
            bot.delete_message(game.chat_id, game.message_id)
            markup = types.ReplyKeyboardRemove(selective=True)
            mention = game.gen_mention()
            bot.send_message(game.chat_id, f"<i>{mention} вышел из игры.</i>",
                             reply_markup=markup, parse_mode="HTML", disable_notification=True)
            if len(game.players) == 1:
                game.end_of_game()
            else:
                game.delete_bot_messages()
                mention = game.gen_mention(game.who_move)
                msg = bot.send_message(game.chat_id, f"Игра продолжается. \n"
                                                     f"{mention}, продолжай:",
                                       reply_markup=markup, parse_mode="HTML", disable_notification=True)
                game.messages_to_delete.append(msg.message_id)
            game.dump()
        else:
            game.users[str(game.user_id)].want_fold = True
            if game.can_move():
                markup = game.gen_keyboard_in_game_selective()
            else:
                markup = gen_keyboard_in_game_for_any()
            mention = game.get_player_short_name()
            msg = bot.send_message(game.chat_id,
                                   f'{mention}, ты точно хочешь сдаться?\nОтправь еще раз "/fold" или "Сдаюсь"',
                                   reply_markup=markup, parse_mode="HTML", disable_notification=True)
            markup = game.gen_keyboard_in_game_selective()
            mention = game.gen_mention(game.who_move)
            msg2 = bot.send_message(game.chat_id, f"Игра продолжается. \n"
                                                  f"{mention}, продолжай:",
                                    reply_markup=markup, parse_mode="HTML", disable_notification=True)
            game.messages_to_delete.extend([game.message_id, msg.message_id, msg2.message_id])
            game.dump()
    else:
        bot.delete_message(game.chat_id, game.message_id)


@bot.message_handler(content_types=['text'], func=lambda message: True if message.text in card_suits else False)
def cmd_choice_suite(message: types.Message):
    game = Game(message)
    if game.in_game and game.can_move() and game.get_move_card_count() != 0:
        if game.get_last_card()[0] == "J":
            last_card = game.pre_joker_card()
        else:
            last_card = game.get_last_card()
        if last_card[0] == "Д":
            markup = gen_keyboard_in_game_for_any()
            bot.send_message(game.chat_id, f"<i>{game.get_player_short_name()} заказывает:</i> {game.text}",
                             reply_markup=markup, disable_notification=True, parse_mode="HTML")
            game.end_move(game.text)
            game.dump()
    else:
        bot.delete_message(game.chat_id, game.message_id)


# РАЗНОЕ:
@bot.message_handler(commands=["help"])
def cmd_help(message: types.Message):
    msg = bot.send_message(message.chat.id, help_text)
    if message.chat.type in ["group", "supergroup"]:
        game = Game(message)
        game.messages_to_delete.extend([msg.message_id, message.message_id])
        game.dump()


@bot.message_handler(content_types=['text'], func=lambda message:
                     message.text in ["/start", "/start@game404bot"]
                     and message.chat.type not in ["group", "supergroup"])
def cmd_start(message: types.Message):
    bot.send_message(message.chat.id, "Игра работает только в групповом чате.\n"
                                      "Собери друзей и добавь бота в группу, которая будет являться игровым столом.\n"
                                      "ОБЯЗАТЕЛЬНО с правами администратора для автоудаления ненужных сообщений.\n"
                                      "Здесь Вы можете ознакомиться с правилами игры отправив /help")


@bot.message_handler(commands=["statistics"])
def cmd_statistics(message: types.Message):
    game = Game(message)
    answer = f""
    if game.in_game:
        answer += f"Идет игра №{game.games_count + 1}.\n"
        answer += game.add_players_list()
    else:
        answer += f"Сейчас игра завершена.\nИгр сыграно в чате: {game.games_count}.\n"
        answer += f"\nСписок пользователей:\n"
        answer += game.add_users_list()
    answer += f"\nID стола: {abs(game.chat_id)}.\n"
    msg = bot.send_message(message.chat.id, answer, disable_notification=True, parse_mode="HTML")
    game.messages_to_delete.extend([msg.message_id, game.message_id])
    game.dump()


@bot.message_handler(content_types=['sticker'])
def stick_answer(message: types.Message):
    print(message.chat.username,
          '(' + convert_time(message.date) + '): стикер', message.sticker.emoji,
          ' из набора:', message.sticker.set_name)
    # bot.send_message(message.chat.id, json.dumps(message.json, indent=4))
    if message.sticker.set_name == "game404":
        bot.delete_message(message.chat.id, message.message_id)
    print(message)
    # print(bot.get_chat_user(message.chat.id, message.from_user.id).user)


@bot.message_handler(commands=["test"])
def cmd_test(message: types.Message):
    game = Game(message)
    markup = game.gen_keyboard_in_game_selective()
    mention = game.gen_mention(game.user_id)
    bot.send_message(game.chat_id, f"{mention} эта клава для тебя", reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=["test_deck"])
def cmd_test_deck(message: types.Message):
    game = Game(message)
    for card in test_deck:
        game.users[str(game.user_id)].hand.append(card)
    game.users[str(game.user_id)].hand.sort()
    msg = bot.send_message(game.chat_id, f"OK", parse_mode="HTML")
    game.messages_to_delete.append(msg.message_id)
    game.dump()


bot.polling(none_stop=True, interval=0)