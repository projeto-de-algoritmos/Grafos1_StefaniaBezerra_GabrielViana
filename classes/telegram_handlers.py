#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import sqlalchemy
from telegram import ReplyKeyboardRemove
from db import User
import db
from classes.services import Services

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
    def __delete_dependency(cls, update, task):
        for i in task.dependencies.split(',')[:-1]:
            i = int(i)
            query_loop = db.session.query(User).filter_by(
                id=i, chat=update.message.chat_id)
            task_loop = query_loop.one()
            task_loop.parents = task_loop.parents.replace(
                '{},'.format(task.id), '')
        task.dependencies = ''

    def __set_dependency(self, depids, update, task, bot):
        for depid in depids[1:]:
            if depid.isdigit():
                depid = int(depid)
                query = db.session.query(User).filter_by(id=depid,
                                                         chat=update.message.chat_id)
                try:
                    taskdep = query.one()
                    taskdep.parents += str(task.id) + ','
                except sqlalchemy.orm.exc.NoResultFound:
                    self.services.not_found_message(bot, update, depid)
                    continue

                deplist = task.dependencies.split(',')
                LOGGER.info("Deplist %s", deplist)
                if not self.services.a_is_in_b(update, depid, task):
                    task.dependencies += str(depid) + ','
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
        task = User(chat=update.message.chat_id, name='{}'.format(text),
                    status='TODO', dependencies='', parents='', priority='')
        db.session.add(task)
        db.session.commit()
        bot.send_message(chat_id=update.message.chat_id,
                         text="New task *TODO* [[{}]] {}"
                         .format(task.id, task.name))

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
                task_id = int(i)
                task_id = int(args[0])
                query = db.session.query(User).filter_by(
                    id=task_id, chat=update.message.chat_id)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    self.services.not_found_message(bot, update, task_id)
                    return
                for each_task in task.dependencies.split(',')[:-1]:
                    each_query = db.session.query(User).filter_by(
                        id=int(each_task), chat=update.message.chat_id)
                    each_task = each_query.one()
                    each_task.parents = each_task.parents.replace(
                        '{},'.format(task.id), '')
                db.session.delete(task)
                db.session.commit()
                bot.send_message(chat_id=update.message.chat_id,
                                 text="User [[{}]] deleted".format(task_id))
            else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You must inform the task id")

    def list(self, bot, update):
        message = ''

        message += '📋 User List\n'
        query = db.session.query(User).filter_by(
            parents='', chat=update.message.chat_id).order_by(User.id)
        for task in query.all():
            icon = '🆕'
            if task.status == 'DOING':
                icon = '🔘'
            elif task.status == 'DONE':
                icon = '✔️'

            message += '[[{}]] {} {}\n'.format(task.id, icon, task.name)
            message += self.services.deps_text(task=task,
                                               chat=update.message.chat_id)

        bot.send_message(chat_id=update.message.chat_id, text=message)
        message = ''

        message += '📝 _Status_\n'
        query = db.session.query(User).filter_by(
            status='TODO', chat=update.message.chat_id).order_by(User.id)
        message += '\n🆕 *TODO*\n'
        for task in query.all():
            if task.duedate != None:
                message += '[[{}]] {} -- Delivery date: {}\n'.format(
                    task.id, task.name, task.duedate)
            else:
                message += '[[{}]] {}\n'.format(task.id, task.name)
        query = db.session.query(User).filter_by(
            status='DOING', chat=update.message.chat_id).order_by(User.id)
        message += '\n🔘 *DOING*\n'
        for task in query.all():
            message += '[[{}]] {}\n'.format(task.id, task.name)
        query = db.session.query(User).filter_by(
            status='DONE', chat=update.message.chat_id).order_by(User.id)
        message += '\n✔️ *DONE*\n'
        for task in query.all():
            message += '[[{}]] {}\n'.format(task.id, task.name)

        bot.send_message(chat_id=update.message.chat_id, text=message)

    @classmethod
    def show_priority(cls, bot, update):
        message = ''
        query = db.session.query(User).filter_by(
            chat=update.message.chat_id).order_by(User.id)
        for task in query.all():
            if task.priority == '':
                message += "[[{}]] {} doesn't have priority {}\n".format(task.id, task.name.upper(),
                                                                         task.priority.upper())
            else:
                message += '[[{}]] {} | priority {}\n'.format(task.id, task.name.upper(),
                                                              task.priority.upper())
        bot.send_message(chat_id=update.message.chat_id, text=message)
