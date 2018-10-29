#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setting, sys
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from depsys import app, db
from depsys.models import User


# flask migrate
def main():
    migrate = Migrate(app, db)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()


if __name__ == '__main__':
    # read user input
    action = sys.argv[1]
    # init admin user/password
    if action == 'init':
        item = User.query.filter_by(username='admin').first()
        # switch admin password to default which set in setting.py
        if item:
            item.password = setting.ADMIN_PASS
            db.session.commit()
            db.session.close()
            print("Admin password has been updated to default!")
        # add admin user/password into db when it doesn't exist
        else:
            item = User(username=setting.ADMIN_USER, password=setting.ADMIN_PASS, enable=1)
            db.session.add(item)
            db.session.commit()
            db.session.close()
            print("Added admin user! User/password refer to setting.py")

    # call flask migrate to tack care of any other db action require
    else:
        main()
