"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for
from flask_login import current_user, login_user
from .forms import LoginForm, SignupForm
from .models import db, User
from .import login_manager
import biken.data as dataManager
import datetime
import os
import json
import time
import random
import string


from dotenv import load_dotenv
from oauthlib.oauth2 import WebApplicationClient
import requests


# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


load_dotenv()
# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID", None)
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET", None)
STRAVA_GRANT_TYPE = os.environ.get("STRAVA_GRANT_TYPE", None)
STRAVA_REDIRECT_LINK = os.environ.get("STRAVA_REDIRECT_LINK", None)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User sign-up page.

    GET requests serve sign-up page.
    POST requests validate form & user creation.
    """
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            user = User(
                name=form.name.data,
                userId=randomString,
                email=form.email.data,
                createdOn=datetime.datetime.utcnow(),
                lastLogin=datetime.datetime.utcnow()
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()  # Create new user
            login_user(user)  # Log in as newly created user
            return redirect(url_for('main_bp.home'))
        flash('A user already exists with that email address.')
    return render_template(
        'signup.html',
        title='Create an Account.',
        form=form,
        template='signup-page',
        body="Sign up for a user account."
    )


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home'))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            # Update last login date
            user.lastLogin=datetime.datetime.utcnow()
            db.session.commit()
            return redirect(next_page or url_for('main_bp.home'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template(
        'login.html',
        form=form,
        title='Log in.',
        template='login-page',
        body="Log in with your User account.",
        strava_redirect_link=STRAVA_REDIRECT_LINK
    )


@auth_bp.route("/loginGoogle")
def loginGoogle():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route("/loginGoogle/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google


    user = User.query.filter_by(email=users_email).first()

    # Doesn't exist? Add it to the database.
    if not user:
        randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        newUser = User(
            name=users_name,
            userId=randomString,
            email=users_email,
            createdOn=datetime.datetime.utcnow(),
            lastLogin=datetime.datetime.utcnow()
        )
        newUser.set_password("random")
        db.session.add(newUser)
        db.session.commit()  # Create new user
        login_user(newUser)
    else :
        # Begin user session by logging the user in
        login_user(user)

    # Send user back to homepage
    return redirect(url_for("main_bp.home"))



@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in upon page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))




# STRAVA
@auth_bp.route("/exchange_token")
def stravaToken():
    query_parameters = request.args
    code = query_parameters.get('code')
    scopes = query_parameters.get('scope')

    if scopes!="read,activity:read_all":
        flash("You need to accept all the permissions required")

    token_url="https://www.strava.com/oauth/token"
    payload = {'code': code, 'client_id': STRAVA_CLIENT_ID,'client_secret':STRAVA_CLIENT_SECRET,'grant_type':STRAVA_GRANT_TYPE}
    # Exchange this code for a short lived access_token
    token_response = requests.post(
        token_url,
        data=payload
    )


    if "errors" in token_response.json().keys():
        print("Auth error")
        print("Response:",token_response.json())
        return redirect(url_for('main_bp.home'))

    else :

        data = token_response.json()
        if current_user.is_authenticated:
            # Just adding the strava account to an already logged in user
            current_user.stravaToken=data["access_token"]
            current_user.stravaTokenExpiration=data["expires_at"]  #6 hours after request
            stravaId = data["athlete"]["id"]

            print("Binding Strava account to the user account")


            # Check if the user has already an account with Strava
            existingStravaUser = User.query.filter_by(stravaId=stravaId).first()

            if existingStravaUser:
                print("Need to merge two accounts")
                # Replacing some data from Strava account and transfering the saved itineraries
                stravaAccount = dataManager.mergeAccount(existingStravaUser,current_user)
                login_user(stravaAccount)


            else :
                # Simply add the strava ID
                current_user.stravaId=stravaId
                db.session.commit()  # Store temporary token

            return redirect(url_for('main_bp.activities'))
       
        else:
            # Log the user with the strava credential
            
            stravaId = data["athlete"]["id"]
            userId = "strava_"+str(stravaId)
            user = User.query.filter_by(stravaId=stravaId).first()

            # Doesn't exist? Add it to the database.
            if not user:
                print("Create new user via Strava. Id:",userId)

                newUser = User(
                    name=data["athlete"]["firstname"],
                    userId=userId,
                    createdOn=datetime.datetime.utcnow(),
                    lastLogin=datetime.datetime.utcnow(),
                    stravaId=stravaId,
                    stravaToken=data["access_token"],
                    stravaTokenExpiration=data["expires_at"]
                )
                newUser.set_password("useless")
                db.session.add(newUser)
                db.session.commit()  # Create new user
                login_user(newUser)
                return redirect(url_for('main_bp.home'))

            else :
                print("Login user via Strava")
                current_user.stravaToken=data["access_token"]
                current_user.stravaTokenExpiration=data["expires_at"]  #6 hours after request
                current_user.lastLogin=datetime.datetime.utcnow()

                db.session.commit()  # Store temporary token
                # Begin user session by logging the user in
                login_user(user)

                return redirect(url_for('main_bp.home'))

