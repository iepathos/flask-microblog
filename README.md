# Flask-Microblog
Created by Glen Baker following along with Miguel Grinberg's excellent tutorial which begins here: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

### Things I've added/improved upon from the straight tutorial
+ Using adaptable #!/usr/bin/env python instead of hard coding flask/bin/python as it is in the tutorial.  This is especially helpful moving to different environments and because the virtualenv info is not in the repo, at least not mine and I keep my environments separate from project space with virtualenvwrapper.
+ I updated this microblog with Bootstrap 3
+ I created a manager.py script using Flask-Script and moved the translation and database management scripts introduced by Grinberg in his tutorial into the manager so you can do ./manager.py dbmigrate  or ./manager.py trupdate
