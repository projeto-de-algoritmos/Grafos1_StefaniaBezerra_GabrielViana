import sqlalchemy
import db
from db import Task
from Url import Url
from createIssues import *


class Message:

    str_help = ""
    u = Url()

    def __init__(self):
        self.str_help = """
                         /new NOME
                         /todo ID
                         /doing ID
                         /done ID
                         /delete ID
                         /list
                         /rename ID NOME
                         /dependson ID ID...
                         /duplicate ID
                         /priority ID PRIORITY{low, medium, high}
                         /help
                        """

    @staticmethod
    def get_last_update_id(updates):
        update_ids = []
        for update in updates['result']:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def deps_text(self, task, chat, preceed=''):
        text = ''
        for i in range(len(task.dependencies.split(',')[:-1])):
            line = preceed
            query = db.session.query(Task).filter_by(id=int(task.dependencies.split(',')[:-1][i]), chat=chat)
            dep = query.one()
            icon = '\U0001F195'
            if dep.status == 'DOING':
                icon = '\U000023FA'
            elif dep.status == 'DONE':
                icon = '\U00002611'
            if i + 1 == len(task.dependencies.split(',')[:-1]):
                line += '└── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
                line += self.deps_text(dep, chat, preceed + '    ')
            else:
                line += '├── [[{}]] {} {}\n'.format(dep.id, icon, dep.name)
                line += self.deps_text(dep, chat, preceed + '│   ')
            text += line
        return text

    def handle_updates(self, updates):
        def new_assigment (msg, chat):
            task = Task(chat=chat, name=msg, status='TODO', dependencies='', parents='', priority='')
            db.session.add(task)
            db.session.commit()
            make_github_issue(task.name, '')
            self.u.send_message("New task *TODO* [[{}]] {}".format(task.id, task.name), chat)
            

        def rename_assigment (msg, chat):
            text = ''
            if msg != '':
               if len(msg.split(' ', 1)) > 1:
                   text = msg.split(' ', 1)[1]
                   msg = msg.split(' ', 1)[0]
            if not msg.isdigit():
               self.u.send_message("You must inform the task id", chat)
            else:
               task_id = int(msg)
               query = db.session.query(Task).filter_by(id=task_id, chat=chat)
               try:
                  task = query.one()
               except sqlalchemy.orm.exc.NoResultFound:
                  self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                  return
               if text == '':
                  self.u.send_message("You want to modify task {}, but you didn't provide any new text".format(task_id), chat)
                  return
               old_text = task.name
               task.name = text
               db.session.commit()
               self.u.send_message("Task {} redefined from {} to {}".format(task_id, old_text, text), chat)

        def duplicate_assigment (msg, chat):
            if not msg.isdigit():
                self.u.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                dtask = Task(chat=task.chat, name=task.name, status=task.status, dependencies=task.dependencies,
                             parents=task.parents, priority=task.priority, duedate=task.duedate)
                db.session.add(dtask)
                for t in task.dependencies.split(',')[:-1]:
                    qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                    t = qy.one()
                    t.parents += '{},'.format(dtask.id)
                db.session.commit()
                self.u.send_message("New task *TODO* [[{}]] {}".format(dtask.id, dtask.name), chat)
                

        def delete_assigment(msg, chat):
            if not msg.isdigit():
                self.u.send_message("You must inform the task id", chat)
            else:
                task_id = int(msg)
                query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                try:
                    task = query.one()
                except sqlalchemy.orm.exc.NoResultFound:
                    self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                    return
                for t in task.dependencies.split(',')[:-1]:
                    qy = db.session.query(Task).filter_by(id=int(t), chat=chat)
                    t = qy.one()
                    t.parents = t.parents.replace('{},'.format(task.id), '')
                db.session.delete(task)
                db.session.commit()
                self.u.send_message("Task [[{}]] deleted".format(task_id), chat)

        def todo_assigment (msg, chat):
            id_list = msg.split(" ")
            for id in id_list:
                if not id.isdigit():
                    send_message("You must inform the task id", chat)
                else:
                    task_id = int(id)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    task.status = 'TODO'
                    db.session.commit()
                    send_message("*TODO* task [[{}]] {}".format(task.id, task.name), chat)

        def doing_assigment(msg, chat):
            id_list = msg.split(" ")
            for id in id_list:
                if not id.isdigit():
                    send_message("You must inform the task id", chat)
                else:
                    task_id = int(id)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    task.status = 'DOING'
                    db.session.commit()
                    send_message("*DOING* task [[{}]] {}".format(task.id, task.name), chat)

        def done_assigment(msg, chat):
            id_list = msg.split(" ")
            for id in id_list:
                if not id.isdigit():
                    send_message("You must inform the task id", chat)
                else:
                    task_id = int(id)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    task.status = 'DONE'
                    db.session.commit()
                    send_message("*DONE* task [[{}]] {}".format(task.id, task.name), chat)

        def list_assigment (msg, chat):
            a = ''
            a += '\U0001F4CB Task List\n'
            query = db.session.query(Task).filter_by(parents='', chat=chat).order_by(Task.id)
            for task in query.all():
                icon = '\U0001F195'
                if task.status == 'DOING':
                    icon = '\U000023FA'
                elif task.status == 'DONE':
                    icon = '\U00002611'
                a += '[[{}]] {} {}\n'.format(task.id, icon, task.name)
                a += self.deps_text(task, chat)
            self.u.send_message(a, chat)
            a = ''
            a += '\U0001F4DD _Status_\n'
            query = db.session.query(Task).filter_by(status='TODO', chat=chat).order_by(Task.id)
            a += '\n\U0001F195 *TODO*\n'

            for task in query.all():
                print(task.name)
                a += '[[{}]] {}\n'.format(task.id, task.name)
            query = db.session.query(Task).filter_by(priority='high', chat=chat).order_by(Task.id)
            a += '\U0001F6F0 *HIGH*\n'
            for task in query.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            query = db.session.query(Task).filter_by(priority='medium', chat=chat).order_by(Task.id)
            a += '\U0001F6F0 *MEDIUM*\n'
            for task in query.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            query = db.session.query(Task).filter_by(priority='low', chat=chat).order_by(Task.id)
            a += '\U0001F6F0 *LOW*\n'

            for task in query.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            query = db.session.query(Task).filter_by(status='DOING', chat=chat).order_by(Task.id)
            a += '\n\U000023FA *DOING*\n'
            for task in query.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            query = db.session.query(Task).filter_by(status='DONE', chat=chat).order_by(Task.id)
            a += '\n\U00002611 *DONE*\n'
            for task in query.all():
                a += '[[{}]] {}\n'.format(task.id, task.name)
            self.u.send_message(a, chat)

        def dependson_assigment(msg, chat):
                text = ''
                if msg != '':
                    if len(msg.split(' ', 1)) > 1:
                        text = msg.split(' ', 1)[1]
                    msg = msg.split(' ', 1)[0]
                if not msg.isdigit():
                    self.u.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    if text == '':
                        for i in task.dependencies.split(',')[:-1]:
                            i = int(i)
                            q = db.session.query(Task).filter_by(id=i, chat=chat)
                            t = q.one()
                            t.parents = t.parents.replace('{},'.format(task.id), '')
                        task.dependencies = ''
                        self.u.send_message("Dependencies removed from task {}".format(task_id), chat)
                    else:
                        for depid in text.split(' '):
                            if not depid.isdigit():
                                self.u.send_message("All dependencies ids must be numeric, and not {}".format(depid), chat)
                            else:
                                depid = int(depid)
                                query = db.session.query(Task).filter_by(id=depid, chat=chat)
                                try:
                                    taskdep = query.one()
                                    taskdep.parents += str(task.id) + ','
                                except sqlalchemy.orm.exc.NoResultFound:
                                    self.u.send_message("_404_ Task {} not found x.x".format(depid), chat)
                                    continue
                                deplist = task.dependencies.split(',')
                                if str(depid) not in deplist:
                                    task.dependencies += str(depid) + ','
                    db.session.commit()
                    self.u.send_message("Task {} dependencies up to date".format(task_id), chat)
                    if len(msg.split(' ', 1)) > 1:
                       text = msg.split(' ', 1)[1]
                       msg = msg.split(' ', 1)[0]
                if not msg.isdigit():
                    self.u.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    if text == '':
                        task.priority = ''
                        self.u.send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                    else:
                        if text.lower() not in ['high', 'medium', 'low']:
                            self.u.send_message("The priority *must be* one of the following: high, medium, low", chat)
                        else:
                            task.priority = text.lower()
                            self.u.send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
                    db.session.commit()

        def priority_assigment(msg, chat):
                text = ''
                if msg != '':
                    if len(msg.split(' ', 1)) > 1:
                        text = msg.split(' ', 1)[1]
                    msg = msg.split(' ', 1)[0]
                if not msg.isdigit():
                    self.u.send_message("You must inform the task id", chat)
                else:
                    task_id = int(msg)
                    query = db.session.query(Task).filter_by(id=task_id, chat=chat)
                    try:
                        task = query.one()
                    except sqlalchemy.orm.exc.NoResultFound:
                        self.u.send_message("_404_ Task {} not found x.x".format(task_id), chat)
                        return
                    if text == '':
                        task.priority = ''
                        self.u.send_message("_Cleared_ all priorities from task {}".format(task_id), chat)
                    else:
                        if text.lower() not in ['high', 'medium', 'low']:
                            self.u.send_message("The priority *must be* one of the following: high, medium, low", chat)
                        else:
                            task.priority = text.lower()
                            self.u.send_message("*Task {}* priority has priority *{}*".format(task_id, text.lower()), chat)
                    db.session.commit()

        for update in updates["result"]:
            if 'message' in update:
                message = update['message']
            elif 'edited_message' in update:
                message = update['edited_message']
            else:
                print('Can\'t process! {}'.format(update))
                return

            try:
                text = message["text"]
            except:
                message["text"] = ""

            command = message["text"].split(" ", 1)[0]
            msg = ''
            if len(message["text"].split(" ", 1)) > 1:
                msg = message["text"].split(" ", 1)[1].strip()
            chat = message["chat"]["id"]
            print(command, msg, chat)
            if command == '/new':
                new_assigment(msg, chat)
            elif command == '/rename':
                rename_assigment (msg, chat)
            elif command == '/duplicate':
                duplicate_assigment(msg, chat)
            elif command == '/delete':
                delete_assigment (msg, chat)
            elif command == '/todo':
                todo_assigment(msg, chat)
            elif command == '/doing':
                doing_assigment(msg, chat)
            elif command == '/done':
                done_assigment (msg,chat)
            elif command == '/list':
                list_assigment (msg, chat)
            elif command == '/dependson':
                dependson_assigment (msg, chat)
            elif command == '/priority':
                priority_assigment(msg, chat)
            elif command == '/start':
                self.u.send_message("Welcome! Here is a list of things you can do.", chat)
                self.u.send_message(self.str_help, chat)
            elif command == '/help':
                self.u.send_message("Here is a list of things you can do.", chat)
                self.u.send_message(self.str_help, chat)
            else:
                self.u.send_message("I'm sorry dave. I'm afraid I can't do that.", chat)
