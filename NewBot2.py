#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using nested ConversationHandlers.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, PicklePersistence)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# State definitions for top level conversation
SELECTING_ACTION, ADDING_ATHLETE, ADDING_NAME, SELECTING_FEAT, ADDING_PERFORMANCE, SELECTING_PERFORMANCE, PERFORMANCE = map(chr, range(7))
# State definitions for second level conversation
SELECTING_LEVEL, SELECTING_GENDER = map(chr, range(7, 9))
# State definitions for descriptions conversation
SELECTING_FEATURE, TYPING = map(chr, range(9, 11))
# Meta states
STOPPING, SHOWING = map(chr, range(11, 13))
# Shortcut for ConversationHandler.END
END = ConversationHandler.END

# Different constants for this example
(PARENTS, CHILDREN, SELF, GENDER, MALE, FEMALE, AGE, NAME, START_OVER, FEATURES,
 CURRENT_FEATURE, CURRENT_LEVEL) = map(chr, range(13, 25))


SELECTING_FEAT, ADDING_NAME, ADD_FEATURES  = map(chr, range(25, 28))

WEIGHT, MAXLOAD, LEAD_RP, LEAD_OS, BOULDER_RP, BOULDER_OS, ATHLETES  = map(chr, range(28, 35))


POT_SBARRA, SOSPENSIONI, KILOS, POWER, DIMENSION, SECONDS  = "POT_SBARRA", "SOSPENSIONI", "KILOS", "POWER", "DIMENSION", "SECONDS"

ATHLETE = ""


# Helper
def _name_switcher(level):
    if level == PARENTS:
        return ('Father', 'Mother')
    elif level == CHILDREN:
        return ('Brother', 'Sister')


def _feature_switcher(level):
    if level == AGE:
        return "Age"
    if level == WEIGHT:
        return "Weight"
    elif level == MAXLOAD:
        return "MaxLoad"
    elif level == LEAD_RP:
        return "Lead_Red_Point"
    elif level == LEAD_OS:
        return "Lead_On_Sight"
    elif level == BOULDER_RP:
        return "Boulder_Red_Point"
    elif level == BOULDER_OS:
        return "Boulder_On_Sight"


def _performance_switcher(level):
    if level == POT_SBARRA:
        return "Potenza Trazioni"
    if level == SOSPENSIONI:
        return "Sospensioni"




def show_ath_meta(update, context):
    #Pretty print gathered data.
    def prettyprint_all(user_data, level):
        people = user_data.get(level)
        if not people:
            return '\nNo information yet.'

        text = ''

        for key, value in people.items():
                text += "\n" + key 

                for k, v in value.items():
                    if k != PERFORMANCE:
                        text += "\n" + k + " : " + v 

                text += "\n"

        return text

    def prettyprint_ath(user_data, level, ath):
        people = user_data.get(level)
        if not people:
            return '\nNo information yet.'

        at = people[ath]

        text = ath + "\n"

        for key, value in at.items():
            if key != PERFORMANCE:
                text += "\n" + key + " : " + value 

                text += "\n"

        return text

    ud = context.user_data

    ath = update.message.text
    if ath not in ud[ATHLETES] and ath != "All":
        update.message.reply_text(text="Non ci sono atleti con questo nome. Scrivere \'All\' per visualizzare tutti gli atleti presenti.\n")
        return ask_for_name_input(update, context)

    if ath == "All":
        text = 'Hai salvato i seguenti atleti in rubrica:' + prettyprint_all(ud, ATHLETES)

    else:
        text = 'Metadati per atleta: ' + prettyprint_ath(ud, ATHLETES, ath)

    buttons = [[
        InlineKeyboardButton(text='Indietro', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    #update.callback_query.answer()
    update.message.reply_text(text=text, reply_markup=keyboard)
    ud[START_OVER] = True

    return SHOWING


# Top level conversation callbacks
def start(update, context):
    """Select an action: Adding parent/child or show data."""
    text = 'Puoi aggiungere un atleta, modificare il valore per un atleta e mostrarne i dati collezionati.' \
           '\nPuoi terminarmi quando vuoi inserendo /stop o cliccare Chiudi dal menu principale.' \
           '\nPer farmi ripartire scrivi /start.'
    buttons = [[
        InlineKeyboardButton(text='Aggiungi/Modifica Atleta', callback_data=str(ADDING_ATHLETE)),
        InlineKeyboardButton(text='Aggiungi Performance', callback_data=str(ADDING_PERFORMANCE))
    ], [
        InlineKeyboardButton(text='Mostra Metadati Atleti', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Chiudi', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need do send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text('Ciao, sono TrainBot, ti aiuterò a tenere traccia dei tuoi allenamenti \n'
                                  'e visualizzare le tue performances')
        update.message.reply_text(text=text, reply_markup=keyboard)

    if not context.user_data:
        context.user_data[ATHLETES] = {}

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def adding_self(update, context):
    """Add information about youself."""
    context.user_data[CURRENT_LEVEL] = SELF
    text = 'Okay, please tell me about yourself.'
    button = InlineKeyboardButton(text='Add info', callback_data=str(MALE))
    keyboard = InlineKeyboardMarkup.from_button(button)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return DESCRIBING_SELF


def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, Ciao.')

    return END


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = 'A presto!'
    update.callback_query.edit_message_text(text=text)

    return END


# Second level conversation callbacks
def select_level(update, context):
    """Choose to add a parent or a child."""
    text = 'You may add a parent or a child. Also you can show the gathered data or go back.'
    buttons = [[
        InlineKeyboardButton(text='Add parent', callback_data=str(PARENTS)),
        InlineKeyboardButton(text='Add child', callback_data=str(CHILDREN))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_LEVEL


def select_gender(update, context):
    """Choose to add mother or father."""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    text = 'Please choose, whom to add.'

    male, female = _name_switcher(level)

    buttons = [[
        InlineKeyboardButton(text='Add ' + male, callback_data=str(MALE)),
        InlineKeyboardButton(text='Add ' + female, callback_data=str(FEMALE))
    ], [
        InlineKeyboardButton(text='Show data', callback_data=str(SHOWING)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECTING_GENDER


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END

# Third level callbacks
def select_feature_2(update, context):
    """Select a feature to update for the person."""
    buttons = [[
        InlineKeyboardButton(text='Peso', callback_data=str(WEIGHT)),
        InlineKeyboardButton(text='Età', callback_data=str(AGE)),
        InlineKeyboardButton(text='Max Carico', callback_data=str(MAXLOAD)),
    ],
    [   InlineKeyboardButton(text='Lead RP', callback_data=str(LEAD_RP)),
        InlineKeyboardButton(text='Boulder RP', callback_data=str(BOULDER_RP)),
    ],
    [ 
        InlineKeyboardButton(text='Boulder OS', callback_data=str(BOULDER_OS)),
        InlineKeyboardButton(text='Lead OS', callback_data=str(LEAD_OS)),
    ], 
    [
        InlineKeyboardButton(text='Fatto', callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        context.user_data[FEATURES] = {GENDER: update.callback_query.data}
        text = 'Selezionare un attributo da aggiornare'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Selezionare un attributo da aggiornare'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


def select_performance(update, context):
    """Select a feature to update for the person."""
    buttons = [[
        InlineKeyboardButton(text='Potenza Trazioni', callback_data=str(POT_SBARRA)),
        InlineKeyboardButton(text='Sospensioni', callback_data=str(SOSPENSIONI)),
    ], 
    [
        InlineKeyboardButton(text='Indietro', callback_data=str(END)),
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we collect features for a new person, clear the cache and save the gender
    if not context.user_data.get(START_OVER):
        #context.user_data[FEATURES] = {GENDER: update.callback_query.data}
        text = 'Selezionare un attributo da aggiornare'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    # But after we do that, we need to send a new message
    else:
        text = 'Selezionare un attributo da aggiornare'
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_FEATURE


def ask_for_input(update, context):
    """Prompt user to input data for selected feature."""
    context.user_data[CURRENT_FEATURE] = update.callback_query.data

    if update.callback_query.data in [POT_SBARRA, SOSPENSIONI]:
        text = 'Okay, Scrivi info per {}'.format(_performance_switcher(update.callback_query.data))

    else:
        text = 'Okay, Scrivi info per {}'.format(_feature_switcher(update.callback_query.data))

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING

def ask_for_input_performance(update, context):

    if update.callback_query.data == POT_SBARRA:

        """Prompt user to input data for selected feature."""
        text = 'Okay, Scrivi info per Potenza alla sbarra' \
                '\nAggiungi i kili  (Kg) e la potenza (N) nel modo seguente (presta attenzione):' \
                '\n K:30 P:300, K:59 P:100, ...' \
                '\n puoi aggiungere quante ripetizioni vuoi anche non massimali'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return POWER

    elif update.callback_query.data == SOSPENSIONI:
        text = 'Okay, Scrivi info per Sospensioni su tacche (2 mani)' \
            '\nAggiungi la dimensione  (mm), i kili (Kg) e la durata \ndella performance (s) c ome segue (presta attenzione):' \
            '\n D:10 K:20 S:20, D:6 K:10 S:10, ...' \
            '\n puoi aggiungere quante ripetizioni vuoi anche non massimali'

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)

        return SECONDS
   

def ask_for_name(update, context):
    """Ask athlete name through a button"""
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    buttons = [[
        InlineKeyboardButton(text='Scrivi Nome', callback_data=str(NAME)),
        InlineKeyboardButton(text='Indietro', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Premi "Scrivi Nome" per scrivere il nome. Se è presente nel database verrà aggiornato \naltrimenti verrà creato.\nPremi indietro per tronare al menu principale'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return ADDING_NAME

def ask_for_name_input(update, context):
    """Prompt user to input data for selected feature."""

    text = 'Inserisci il nome dell\'atleta come salvato in rubrica'

    try:
        if update.callback_query.data == SHOWING:
            text += "\nScrivi All per visualizzare tutti gli atleti salvati"

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text)
    
    except:
        text += "\nScrivi All per visualizzare tutti gli atleti salvati"
        update.message.reply_text(text=text)


    return TYPING


def save_input(update, context):
    """Save input for feature and return to feature selection."""
    ud = context.user_data
    ud[FEATURES][ud[CURRENT_FEATURE]] = update.message.text

    ud[START_OVER] = True

    return select_feature(update, context)


def save_name(update, context):
    """Save input for feature and return to feature selection."""
    ud = context.user_data
    ud[CURRENT_FEATURE] = update.message.text
    ud[ATHLETE] = update.message.text

    if ud[CURRENT_FEATURE] not in ud[ATHLETES].keys():
        ud[ATHLETES][ud[CURRENT_FEATURE]] = {}
        text = 'Ho creato un nuovo atleta chiamato: {}'.format(update.message.text)
    else:
        text = 'Hai scelto di aggiornare le informazioni per un atleta presente: {}'.format(update.message.text)

    #ud[START_OVER] = True

    
    update.message.reply_text(text=text)

    buttons = [[
        InlineKeyboardButton(text='Aggiungi Attributi', callback_data=str(ADD_FEATURES)),
        InlineKeyboardButton(text='Indietro', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Per favore, scegli tra le opzioni qui sotto:'
    update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return SELECTING_FEAT


def select_name_for_perf(update, context):
    """Save input for feature and return to feature selection."""
    ud = context.user_data
    ud[CURRENT_FEATURE] = update.message.text
    ud[ATHLETE] = update.message.text

    if ud[CURRENT_FEATURE] not in ud[ATHLETES].keys():
        ud[ATHLETES][ud[CURRENT_FEATURE]] = {}
        ud[ATHLETES][ud[CURRENT_FEATURE]][PERFORMANCE] = {}
        text = 'Ho creato un nuovo atleta chiamato: {}'.format(update.message.text)

    elif PERFORMANCE not in ud[ATHLETES][ud[CURRENT_FEATURE]].keys():
        ud[ATHLETES][ud[CURRENT_FEATURE]][PERFORMANCE] = {}
        text = 'Creo spazio performance per atleta: {}'.format(update.message.text)
    else:
        text = 'Aggiorno performances per l\'atleta: {}'.format(update.message.text)

    #ud[START_OVER] = True

    
    update.message.reply_text(text=text)

    buttons = [[
        InlineKeyboardButton(text='Aggiungi Performance', callback_data=str(PERFORMANCE)),
        InlineKeyboardButton(text='Indietro', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    text = 'Per favore, scegli tra le opzioni qui sotto:'
    update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False

    return SELECTING_PERFORMANCE

def save_input_feature(update, context):
    """Save input for feature and return to feature selection."""
    ud = context.user_data
    level = _feature_switcher(ud[CURRENT_FEATURE])

    print("level: {}, athlete: {}".format(level, ud[ATHLETE]))
    #level = update.callback_query.data
    ud[ATHLETES][ud[ATHLETE]][level] = update.message.text

    print(ud)

    ud[START_OVER] = True

    return select_feature_2(update, context)


def save_input_performance(update, context):
    """Save input for performance and return to performance selection."""
    ud = context.user_data
    level = ud[CURRENT_FEATURE]

    print("level: {}, athlete: {}".format(level, ud[ATHLETE]))
    #level = update.callback_query.data
    ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][level] = update.message.text

    print(ud)

    ud[START_OVER] = True

    return select_performance(update, context)


def save_power(update, context):
    """ Save Power in the appropriate format """

    ud = context.user_data

    #if it is the first time create the dict
    if POT_SBARRA not in ud[ATHLETES][ud[ATHLETE]][PERFORMANCE].keys():
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA] = {}


    date_ = str(datetime.date.today().day) + "/" + str(datetime.date.today().month) + "/" + str(datetime.date.today().day)

    kilos = []
    power =  []
    data = update.message.text

    data = data.split(",")
    data = [i.split(' ') for i in data]
    for subset in data:
        for item in subset:
            if item != ''  or item != ' ':
                if "K" in item:
                    kilos.append(float(item.split("K:")[1]))
                elif "P" in item:
                    power.append(float(item.split("P:")[1]))

    if date_ in ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA].keys():
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA][date_][KILOS] = ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA][date_][KILOS] + kilos
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA][date_][POWER] = ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA][date_][POWER] + power

    else:
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][POT_SBARRA][date_] = {KILOS: kilos, POWER: power}

    ud[START_OVER] = True

    return select_performance(update, context)

def save_sosp(update, context):
    """ Save Power in the appropriate format """

    ud = context.user_data

    #if it is the first time create the dict
    if SOSPENSIONI not in ud[ATHLETES][ud[ATHLETE]][PERFORMANCE].keys():
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI] = {}


    date_ = str(datetime.date.today().day) + "/" + str(datetime.date.today().month) + "/" + str(datetime.date.today().day)

    dimension = []
    kilos = []
    seconds =  []
    data = update.message.text

    data = data.split(",")
    data = [i.split(' ') for i in data]
    for subset in data:
        for item in subset:
            if item != ''  or item != ' ':
                if "D" in item:
                    dimension.append(float(item.split("D:")[1]))
                if "K" in item:
                    kilos.append(float(item.split("K:")[1]))
                elif "S" in item:
                    seconds.append(float(item.split("S:")[1]))

    if date_ in ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI].keys():
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][KILOS] = ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][KILOS] + kilos
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][DIMENSION] = ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][DIMENSION] + dimension
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][SECONDS] = ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_][SECONDS] + seconds

    else:
        ud[ATHLETES][ud[ATHLETE]][PERFORMANCE][SOSPENSIONI][date_] = {DIMENSION: dimension, KILOS: kilos, SECONDS: seconds}

    print(ud)

    ud[START_OVER] = True

    return select_performance(update, context)




def end_describing(update, context):
    """End gathering of features and return to parent conversation."""
    ud = context.user_data
    level = ud[CURRENT_LEVEL]

    """
    # Print upper level menu
    if level == SELF:
        ud[START_OVER] = True
        start(update, context)
    else:
        select_level(update, context)

    """
    ud[START_OVER] = True
    ask_for_name(update, context)

    return END


def stop_nested(update, context):
    """Completely end conversation from within nested conversation."""
    update.message.reply_text('Okay, bye.')

    return STOPPING



def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater("1117019452:AAFKKcCCm4VVl4t6WB7vnGHulsYLY-6BvBI", persistence=pp, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Set up third level ConversationHandler (collecting features)
    description_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_feature_2, pattern='^' + str(ADD_FEATURES) + '$')],

        states={
            SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input,
                                                     pattern='^' + str(AGE) + '$|^' + str(WEIGHT) + '$|^' + str(MAXLOAD) + '$|^' + str(LEAD_OS) + '$|^' + str(LEAD_RP) + '$|^' + str(BOULDER_RP) + '$|^' + str(BOULDER_OS) + '$')],
            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input_feature)],
        },

        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # Return to second level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: STOPPING,
        }
    )

    # Set up third level ConversationHandler (collecting features)
    performances_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_performance, pattern='^' + str(PERFORMANCE) + '$')],

        states={
            SELECTING_FEATURE: [CallbackQueryHandler(ask_for_input_performance,
                                                     pattern='^' + str(POT_SBARRA) + '$|^' + str(SOSPENSIONI) + '$')],


            POWER : [MessageHandler(Filters.text & ~Filters.command, save_power)],
            SECONDS : [MessageHandler(Filters.text & ~Filters.command, save_sosp)],

            #TYPING: [MessageHandler(Filters.text & ~Filters.command, save_input_performance)],
        },

        fallbacks=[
            CallbackQueryHandler(end_describing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # Return to second level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: STOPPING,
        }
    )


    # Set up second level ConversationHandler (adding a person)
    add_athlete_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_name,
                                           pattern='^' + str(ADDING_ATHLETE) + '$')],
        states={
            
            ADDING_NAME: [CallbackQueryHandler(ask_for_name_input,
                                                     pattern='^' + str(NAME) + '$')],

            TYPING: [MessageHandler(Filters.text & ~Filters.command, save_name)],

            SELECTING_FEAT : [description_conv]

        },

        fallbacks=[
            #CommandHandler('back', end_second_level),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: END,
        }
    )


    # Set up second level ConversationHandler (adding a person)
    show_athletes = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_name_input,
                                           pattern='^' + str(SHOWING) + '$')],
        states={

            TYPING: [MessageHandler(Filters.text & ~Filters.command, show_ath_meta)],

        },

        fallbacks=[
            #CommandHandler('back', end_second_level),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: END,
        }
    )

    # Set up second level ConversationHandler (adding a person)
    add_performance = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_name,
                                           pattern='^' + str(ADDING_PERFORMANCE) + '$')],
        states={

            ADDING_NAME: [CallbackQueryHandler(ask_for_name_input,
                                                     pattern='^' + str(NAME) + '$')],

            TYPING: [MessageHandler(Filters.text & ~Filters.command, select_name_for_perf)],

            SELECTING_PERFORMANCE : [performances_conv]

        },

        fallbacks=[
            #CommandHandler('back', end_second_level),
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # After showing data return to top level menu
            SHOWING: SHOWING,
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOPPING: END,
        }
    )

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the econd level
    # conversation, we need to make sure the top level conversation can also handle them
    selection_handlers = [
        add_athlete_conv,
        #CallbackQueryHandler(show_data, pattern='^' + str(SHOWING) + '$'),
        show_athletes,
        #CallbackQueryHandler(adding_self, pattern='^' + str(ADDING_SELF) + '$'),
        add_performance,
        CallbackQueryHandler(end, pattern='^' + str(END) + '$'),
    ]
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SHOWING: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            STOPPING: [CommandHandler('start', start)],
        },

        fallbacks=[CommandHandler('stop', stop)],

        name="top_level",
        persistent=True
    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()