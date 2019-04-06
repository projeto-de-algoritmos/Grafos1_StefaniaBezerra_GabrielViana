#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import sqlalchemy
from telegram import ReplyKeyboardRemove
from db import User
import db
from classes.services import Services
import twitter

TUTORIAL = "https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/"

HELP = """
 /new NAME
 /delete ID
 /list

 /help
 /help_github_token
"""

FORMAT = '%(asctime)s -- %(levelname)s -- %(module)s %(lineno)d -- %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
LOGGER = logging.getLogger('root')
LOGGER.info("Running %s", sys.argv[0])


class Handler(object):
    def __init__(self):
        self.services = Services()

    @classmethod
    def auth():
        return twitter.Api(consumer_key='i9d3USYOnSST9icTKv5KP4VT2',
                          consumer_secret='Xv3mtlsyksSC16efsva4izjnEKwWHevgTVKEarAHVZBw0cLsxE',
                          access_token_key='198884980-hXTcHPBX7ZD2fPWf97Xl80mOw2O2QIaP7RigrrbE',
                          access_token_secret='qCi0D867Qw0ZpdpY8enxZtf11TIkQiyYK4uI0JR7ryjo1')

    @classmethod
    def __delete_dependency(cls, update, user):
        for i in user.dependencies.split(',')[:-1]:
            i = int(i)
            query_loop = db.session.query(User).filter_by(
                id=i, chat=update.message.chat_id)
            user_loop = query_loop.one()
            user_loop.parents = user_loop.parents.replace(
                '{},'.format(user.id), '')
        user.dependencies = ''

    def __set_dependency(self, depids, update, user, bot):
        for depid in depids[1:]:
            if depid.isdigit():
                depid = int(depid)
                query = db.session.query(User).filter_by(id=depid,
                                                         chat=update.message.chat_id)
                try:
                    userdep = query.one()
                    userdep.parents += str(user.id) + ','
                except sqlalchemy.orm.exc.NoResultFound:
                    self.services.not_found_message(bot, update, depid)
                    continue

                deplist = user.dependencies.split(',')
                LOGGER.info("Deplist %s", deplist)
                if not self.services.a_is_in_b(update, depid, user):
                    user.dependencies += str(depid) + ','
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text="User {} dependencies up to date".format(depid))
                else:
                    bot.send_message(chat_id=update.message.chat_id,
                                     text="{} is dependence on some of these numbers.".format(depid))
            else:
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text="All dependencies ids must be numeric, and not {}"
                    .format(depid))

    @classmethod
    def start(cls, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Welcome! Here is a list of things you can do.")
        bot.send_message(chat_id=update.message.chat_id,
                         text="{}".format(HELP))

    @classmethod
    def new(cls, bot, update, args):
        text = ''
        for each_word in args:
            text += each_word + ' '

        user = User(chat=update.message.chat_id, screen_name='{}'.format(text),
                    friends='', tweet_id='')

        api = twitter.Api(consumer_key='',
                          consumer_secret='',
                          access_token_key='',
                          access_token_secret='')

        statuses = api.GetFriends(screen_name='{}'.format(text))
        # print([s.text for s in statuses])


        db.session.add(user)
        db.session.commit()
        messages = []
        for s in statuses:
            message = s.AsDict().get('name')
            messages.append(message)

        bot.send_message(chat_id=update.message.chat_id,
                        text="Username[[{}]] {}"
                        .format(user.id, user.screen_name) +'abigo stoaki:' + str(messages))

    
    def echo(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="I'm sorry, {}. I'm afraid I can't do {}."
                         .format(self.services.get_name(update), update.message.text))
        bot.send_message(chat_id=update.message.chat_id,
                         text="{}".format(HELP))

    @classmethod
    def help(cls, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Welcome! Here is a list of things you can do.")
        bot.send_message(chat_id=update.message.chat_id,
                         text="{}".format(HELP))

    def delete(self, bot, update, args):
        for i in args:
            if i.isdigit():
                user_id = int(i)
                user_id = int(args[0])
                query = db.session.query(User).filter_by(
                    id=user_id, chat=update.message.chat_id)
                try:
                    user = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    self.services.not_found_message(bot, update, user_id)
                    return
                for each_user in user.dependencies.split(',')[:-1]:
                    each_query = db.session.query(User).filter_by(
                        id=int(each_user), chat=update.message.chat_id)
                    each_user = each_query.one()
                    each_user.parents = each_user.parents.replace(
                        '{},'.format(user.id), '')
                db.session.delete(user)
                db.session.commit()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User [[{}]] deleted".format(user_id))
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You must inform the user id")

    def list(self, bot, update):
        message = ''

        message += '📋 User List\n'
        query = db.session.query(User).filter_by(
            friends='', chat=update.message.chat_id).order_by(User.id)
        for user in query.all():
            icon = '🆕'

            message += '[[{}]] {} {}\n'.format(user.id, icon, user.screen_name)
            message += self.services.deps_text(user=user,
                                               chat=update.message.chat_id)

        bot.send_message(chat_id=update.message.chat_id, text=message)
        message = ''

        message += '📝 _Status_\n'
        query = db.session.query(User).filter_by(
            status='TODO', chat=update.message.chat_id).order_by(User.id)
        message += '\n🆕 *TODO*\n'
        for user in query.all():
            if user.duedate != None:
                message += '[[{}]] {} -- Delivery date: {}\n'.format(
                    user.id, user.name, user.duedate)
            else:
                message += '[[{}]] {}\n'.format(user.id, user.name)
        query = db.session.query(User).filter_by(
            status='DOING', chat=update.message.chat_id).order_by(User.id)
        message += '\n🔘 *DOING*\n'
        for user in query.all():
            message += '[[{}]] {}\n'.format(user.id, user.name)
        query = db.session.query(User).filter_by(
            status='DONE', chat=update.message.chat_id).order_by(User.id)
        message += '\n✔️ *DONE*\n'
        for user in query.all():
            message += '[[{}]] {}\n'.format(user.id, user.name)

        bot.send_message(chat_id=update.message.chat_id, text=message)

    @classmethod
    def show_priority(cls, bot, update):
        message = ''
        query = db.session.query(User).filter_by(
            chat=update.message.chat_id).order_by(User.id)
        for user in query.all():
            if user.priority == '':
                message += "[[{}]] {} doesn't have priority {}\n".format(user.id, user.name.upper(),
                                                                         user.priority.upper())
            else:
                message += '[[{}]] {} | priority {}\n'.format(user.id, user.name.upper(),
                                                              user.priority.upper())
        bot.send_message(chat_id=update.message.chat_id, text=message)
