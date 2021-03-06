from __future__ import unicode_literals

from flask_dance.consumer import OAuth2ConsumerBlueprint
from functools import partial
from flask.globals import LocalProxy, _lookup_app_object

try:
    from flask import _app_ctx_stack as stack
except ImportError:
    from flask import _request_ctx_stack as stack

__maintainer__ = "Josh Cullum <josh.cullum@eggplant.io>"


def make_cognito_blueprint(
    client_id=None,
    client_secret=None,
    scope=None,
    redirect_url=None,
    redirect_to=None,
    login_url=None,
    authorized_url=None,
    session_class=None,
    storage=None,
    domain_name=None,
    aws_region=None,
):
    """
    Make a blueprint for authenticating with Cognito using OAuth 2. This requires
    a client ID, client secret, domain name and AWS Region from Cognito. You should either pass them to
    this constructor, or make sure that your Flask application config defines
    them, using the variables
    :envvar:`COGNITO_OAUTH_CLIENT_ID`
    :envvar:`COGNITO_OAUTH_CLIENT_SECRET`
    Args:
        domain_name (str): The Cognito Domain prefix for your cognito user pool
        aws_region (str): The AWS Region that cognito is set to use
        client_id (str): The client ID for your application on Cognito.
        client_secret (str): The client secret for your application on Cognito
        scope (str, optional): comma-separated list of scopes for the OAuth token
        redirect_url (str): the URL to redirect to after the authentication
            dance is complete
        redirect_to (str): if ``redirect_url`` is not defined, the name of the
            view to redirect to after the authentication dance is complete.
            The actual URL will be determined by :func:`flask.url_for`
        login_url (str, optional): the URL path for the ``login`` view.
            Defaults to ``/cognito``
        authorized_url (str, optional): the URL path for the ``authorized`` view.
            Defaults to ``/cognito/authorized``.
        session_class (class, optional): The class to use for creating a
            Requests session. Defaults to
            :class:`~flask_dance.consumer.requests.OAuth2Session`.
        storage: A token storage class, or an instance of a token storage
                class, to use for this blueprint. Defaults to
                :class:`~flask_dance.consumer.storage.session.SessionStorage`.
    :rtype: :class:`~flask_dance.consumer.OAuth2ConsumerBlueprint`
    :returns: A :ref:`blueprint <flask:blueprints>` to attach to your Flask app.
    """
    scope = scope or ["openid", "profile"]
    aws_region = aws_region or "us-east-1"

    cognito_bp = OAuth2ConsumerBlueprint(
        "cognito",
        __name__,
        client_id=client_id,
        client_secret=client_secret,
        base_url="https://{domain_name}.auth.{aws_region}.amazoncognito.com".format(
            domain_name=domain_name, aws_region=aws_region
        ),
        authorization_url="https://{domain_name}.auth.{aws_region}.amazoncognito.com/oauth2/authorize".format(
            domain_name=domain_name, aws_region=aws_region
        ),
        token_url="https://{domain_name}.auth.{aws_region}.amazoncognito.com/oauth2/token".format(
            domain_name=domain_name, aws_region=aws_region
        ),
        scope=scope,
        redirect_url=redirect_url,
        redirect_to=redirect_to,
        login_url=login_url,
        authorized_url=authorized_url,
        session_class=session_class,
        storage=storage,
    )
    cognito_bp.from_config["client_id"] = "COGNITO_OAUTH_CLIENT_ID"
    cognito_bp.from_config["client_secret"] = "COGNITO_OAUTH_CLIENT_SECRET"

    @cognito_bp.before_app_request
    def set_applocal_session():
        ctx = stack.top
        ctx.cognito_oauth = cognito_bp.session

    return cognito_bp


cognito = LocalProxy(partial(_lookup_app_object, "cognito_oauth"))
