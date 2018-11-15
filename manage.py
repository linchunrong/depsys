#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setting, sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from depsys import app, db
from depsys.models import User, Role


# flask migrate
def main():
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()


# init role db
def role_init(name, describe):
    """Init admin role"""
    item = Role.query.filter_by(name=name).first()
    if item:
        return item.role_id
    else:
        item = Role(name=name, describe=describe)
        db.session.add(item)
        db.session.commit()
        db.session.close()
        new = Role.query.filter_by(name=name).first()
        role_id = new.role_id
        return role_id


if __name__ == '__main__':
    # read user input
    action = sys.argv[1]
    # init admin user/password
    if action == 'init':
        # init role db, three roles by default
        admin_role = role_init(name='admin', describe='administrator')
        editor_role = role_init(name='editor', describe='writeable')
        user_role = role_init(name='user', describe='readonly')
        print("Role has been init!")
        item = User.query.filter_by(username='admin').first()
        # switch admin password to default which set in setting.py
        if item:
            item.password = setting.ADMIN_PASS
            item.role = admin_role
            db.session.commit()
            db.session.close()
            print("Admin password has been updated to default!")
        # add admin user/password into db when it doesn't exist
        else:
            item = User(username=setting.ADMIN_USER, password=setting.ADMIN_PASS, enable=1, role=admin_role)
            db.session.add(item)
            db.session.commit()
            db.session.close()
            print("Added admin user! User/password refer to setting.py")

    # call flask migrate to tack care of any other db action require
    else:
        main()
