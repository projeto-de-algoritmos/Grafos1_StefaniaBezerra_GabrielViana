#!/usr/bin/env python3

from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from classes.telegram_handlers import Handler


class HandlerUpdater(object):
    def __init__(self, token):
        self.token = token
        self.updater = Updater(token='{}'.format(self.token))
        self.dispatcher = self.updater.dispatcher

    @classmethod
    def __command_handlers_github(cls, task_command):
        handler = Handler()
        command_handler = None
        if task_command == 'my_github_token_handler':
            command_handler = CommandHandler('my_github_token_handler', handler.my_github_token, pass_args=True)
        elif task_command == 'send_issue_handler':
            command_handler = CommandHandler('send_issue', handler.send_issue, pass_args=True)
        return command_handler

    @classmethod
    def __command_handlers_show(cls, task_command):
        handler = Handler()
        command_handler = None
        if task_command == 'start_handler':
            command_handler = CommandHandler('start', handler.start)
        elif task_command == 'help_handler':
            command_handler = CommandHandler('help', handler.help)
        elif task_command == 'list_handler':
            command_handler = CommandHandler('list', handler.list)
        elif task_command == 'echo_handler':
            command_handler = MessageHandler(Filters.text, handler.echo)
        return command_handler

    @classmethod
    def __command_handlers_pass_args(cls, task_command):
        handler = Handler()
        command_handler = None
        if task_command == 'new_handler':
            command_handler = CommandHandler('new_user', handler.new, pass_args=True)
        elif task_command == 'delete_handler':
            command_handler = CommandHandler('remove_user', handler.delete, pass_args=True)
        return command_handler

    @classmethod
    def __command_handlers_callback(cls, task_command):
        handler = Handler()
        command_handler = None
        if task_command == 'add_date_callback':
            command_handler = CallbackQueryHandler(handler.add_date_function)
        return command_handler

    def add_handlers(self):
        self.dispatcher.add_handler(self.__command_handlers_pass_args('new_handler'))
        self.dispatcher.add_handler(self.__command_handlers_pass_args('delete_handler'))
        self.dispatcher.add_handler(self.__command_handlers_show('start_handler'))
        self.dispatcher.add_handler(self.__command_handlers_show('help_handler'))
        self.dispatcher.add_handler(self.__command_handlers_show('list_handler'))
        self.dispatcher.add_handler(self.__command_handlers_show('echo_handler'))

    def updater_start_polling(self):
        self.updater.start_polling()
