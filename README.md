# flask-authentication

Authentication of web-applications using Flask. This is a template to be used in Flask applications.

### Creating the database

The creation of the database uses Flask-Migrate. This also handles the database migrations (changing database schemes). This template uses a sqlite database.

Make sure to set the environment variable of your shell for the Flask application as:

```shell
export FLASK_APP='app.py'
```

To create a migration repository and initialize the database run:

```shell
flask db init
```

To generate the initial migration run:

```shell
flask db migrate -m "Initial migration."
```

To apply the migrations to the database (and to also establish the initial database) run:

```shell
flask db upgrade
```

Note: The migration script needs to be reviewed and edited, as Alembic currently does not detect every change you make to your models. In particular, Alembic is currently unable to detect table name changes, column name changes, or anonymously named constraints.

For more information check out: [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
