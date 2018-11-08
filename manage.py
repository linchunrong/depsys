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
def role_init_admin():
    """Init admin role"""
    item = Role.query.filter_by(name='admin').first()
    if item:
        return item.role_id
    else:
        item = Role(name='admin', describe='administrator')
        db.session.add(item)
        db.session.commit()
        db.session.close()
        new = Role.query.filter_by(name='admin').first()
        role_id = new.role_id
        return role_id


if __name__ == '__main__':
    # read user input
    action = sys.argv[1]
    # init admin user/password
    if action == 'init':
        item = User.query.filter_by(username='admin').first()
        role = role_init_admin()
        # switch admin password to default which set in setting.py
        if item:
            item.password = setting.ADMIN_PASS
            item.role = role
            db.session.commit()
            db.session.close()
            print("Admin password has been updated to default!")
        # add admin user/password into db when it doesn't exist
        else:
            item = User(username=setting.ADMIN_USER, password=setting.ADMIN_PASS, enable=1, role=role)
            db.session.add(item)
            db.session.commit()
            db.session.close()
            print("Added admin user! User/password refer to setting.py")

    # call flask migrate to tack care of any other db action require
    else:
        main()
