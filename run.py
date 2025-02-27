import logging
import os
from json import loads

import structlog
from alembic import command
from alembic.config import Config
from flask import Flask, _app_ctx_stack
from flask_cors import CORS
from pika.exceptions import AMQPConnectionError
from retrying import RetryError, retry
from sqlalchemy import create_engine, column, text
from sqlalchemy.exc import ProgrammingError, DatabaseError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import exists, select

from application.logger_config import logger_initial_config


logger = structlog.wrap_logger(logging.getLogger(__name__))


def create_app(config=None, init_db=True, init_rabbit=True):
    # create and configure the Flask application
    app = Flask(__name__)
    app.name = "ras-collection-instrument"
    config_name = config or os.environ.get('APP_SETTINGS', 'Config')
    app_config = f"config.{config_name}"
    app.config.from_object(app_config)

    # register view blueprints
    from application.views.survey_responses_view import survey_responses_view
    app.register_blueprint(survey_responses_view, url_prefix='/survey_response-api/v1')
    from application.views.collection_instrument_view import collection_instrument_view
    app.register_blueprint(collection_instrument_view, url_prefix='/collection-instrument-api/1.0.2')
    from application.views.info_view import info_view
    app.register_blueprint(info_view)
    from application.error_handlers import error_blueprint
    app.register_blueprint(error_blueprint)

    CORS(app)

    logger_initial_config(service_name='ras-collection-instrument', log_level=app.config['LOGGING_LEVEL'])
    logger.info("Logging configured", log_level=app.config['LOGGING_LEVEL'])

    with open(app.config['COLLECTION_EXERCISE_SCHEMA']) as io:
        app.config['COLLECTION_EXERCISE_SCHEMA'] = loads(io.read())

    if init_db:
        try:
            initialise_db(app)
        except RetryError:
            logger.exception('Failed to initialise database')
            exit(1)
    else:
        logger.debug('Skipped initialising database')

    if init_rabbit:
        try:
            initialise_rabbit(app)
        except RetryError:
            logger.exception('Failed to initialise rabbitmq')
            exit(1)
    else:
        logger.debug('Skipped initialising rabbitmq')

    logger.info("App setup complete", config=config_name)

    return app


def create_database(db_connection, db_schema):
    from application.models import models

    def current_request():
        return _app_ctx_stack.__ident_func__()

    engine = create_engine(db_connection)
    session = scoped_session(sessionmaker(), scopefunc=current_request)
    session.configure(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    engine.session = session

    if db_connection.startswith('postgres'):

        for t in models.Base.metadata.sorted_tables:
            t.schema = db_schema

        schemata_exists = exists(select([column('schema_name')])
                                 .select_from(text("information_schema.schemata"))
                                 .where(text(f"schema_name = '{db_schema}'")))

        alembic_cfg = Config("alembic.ini")

        if not session().query(schemata_exists).scalar():
            logger.info("Creating schema ", db_schema=db_schema)
            engine.execute(f"CREATE SCHEMA {db_schema}")
            logger.info("Creating database tables.")
            models.Base.metadata.create_all(engine)
            # If the db is created from scratch we don't need to update with alembic,
            # however we do need to record (stamp) the latest version for future migrations
            command.stamp(alembic_cfg, "head")
        else:
            logger.info("Updating database with Alembic")
            command.upgrade(alembic_cfg, "head")

    else:
        logger.info("Creating database tables")
        models.Base.metadata.create_all(engine)

    logger.info("Ok, database tables have been created")
    return engine


def retry_if_database_error(exception):
    logger.error(exception)
    return isinstance(exception, DatabaseError) and not isinstance(exception, ProgrammingError)


@retry(retry_on_exception=retry_if_database_error, wait_fixed=2000, stop_max_delay=30000, wrap_exception=True)
def initialise_db(app):
    # TODO: this isn't entirely safe, use a get_db() lazy initializer instead...
    app.db = create_database(app.config['DATABASE_URI'],
                             app.config['DATABASE_SCHEMA'])


def retry_if_rabbit_connection_error(exception):
    return isinstance(exception, AMQPConnectionError)


@retry(retry_on_exception=retry_if_rabbit_connection_error, wait_fixed=2000, stop_max_delay=60000, wrap_exception=True)
def initialise_rabbit(app):
    from application.controllers import collection_instrument
    from application.controllers import survey_response

    with app.app_context():
        collection_instrument.CollectionInstrument.initialise_messaging()
        survey_response.SurveyResponse.initialise_messaging()


if __name__ == '__main__':
    app = create_app()

    scheme, host, port = app.config['SCHEME'], app.config['HOST'], int(app.config['PORT'])

    app.run(debug=app.config['DEBUG'], host=host, port=port)
