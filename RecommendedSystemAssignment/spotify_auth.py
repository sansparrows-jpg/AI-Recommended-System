# SoundScope - Spotify Authorization Helper

import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


# Spotify OAuth endpoints.
SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

# Permissions needed for full playback and playback control.
SPOTIFY_SCOPES = " ".join(
    [
        "streaming",
        "user-read-email",
        "user-read-private",
        "user-read-playback-state",
        "user-modify-playback-state",
    ]
)


def get_spotify_settings():
    """
    Read Spotify credentials from .streamlit/secrets.toml.
    """

    required_keys = [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI",
    ]

    missing = [
        key
        for key in required_keys
        if key not in st.secrets
        or not str(st.secrets[key]).strip()
    ]

    if missing:
        raise RuntimeError(
            "Missing Spotify setting(s): "
            + ", ".join(missing)
            + ". Add them to .streamlit/secrets.toml."
        )

    return {
        "client_id":
            str(st.secrets["SPOTIFY_CLIENT_ID"]).strip(),

        "client_secret":
            str(st.secrets["SPOTIFY_CLIENT_SECRET"]).strip(),

        "redirect_uri":
            str(st.secrets["SPOTIFY_REDIRECT_URI"]).strip(),
    }


def _base64url_encode(value):
    """
    Encode bytes into URL-safe text without = padding.
    """

    return (
        base64.urlsafe_b64encode(value)
        .decode("utf-8")
        .rstrip("=")
    )


def _base64url_decode(value):
    """
    Decode URL-safe Base64 text.
    """

    padding = "=" * (
        (-len(value)) % 4
    )

    return base64.urlsafe_b64decode(
        value + padding
    )


def _create_signed_state():
    """
    Create a short-lived signed OAuth state.

    It also carries the current SoundScope login identity.
    This lets us restore the user's SoundScope session after
    Spotify redirects the browser back to Streamlit.
    """

    settings = get_spotify_settings()

    payload = {
        "timestamp":
            int(time.time()),

        "nonce":
            secrets.token_urlsafe(16),

        "user_id":
            st.session_state.get(
                "user_id"
            ),

        "username":
            st.session_state.get(
                "username"
            ),

        "role":
            st.session_state.get(
                "role"
            ),
    }

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    encoded_payload = _base64url_encode(
        payload_bytes
    )

    signature = hmac.new(
        settings["client_secret"].encode(
            "utf-8"
        ),
        encoded_payload.encode(
            "utf-8"
        ),
        hashlib.sha256,
    ).digest()

    return (
        encoded_payload
        + "."
        + _base64url_encode(
            signature
        )
    )


def _verify_signed_state(state):
    """
    Verify the OAuth state and return its payload.

    State expires after 10 minutes.
    """

    settings = get_spotify_settings()

    try:
        encoded_payload, encoded_signature = (
            str(state).split(
                ".",
                1,
            )
        )

        expected_signature = hmac.new(
            settings["client_secret"].encode(
                "utf-8"
            ),
            encoded_payload.encode(
                "utf-8"
            ),
            hashlib.sha256,
        ).digest()

        received_signature = (
            _base64url_decode(
                encoded_signature
            )
        )

        if not hmac.compare_digest(
            expected_signature,
            received_signature,
        ):
            return None

        payload = json.loads(
            _base64url_decode(
                encoded_payload
            ).decode("utf-8")
        )

        timestamp = int(
            payload.get(
                "timestamp",
                0,
            )
        )

        if (
            timestamp <= 0
            or time.time() - timestamp > 600
        ):
            return None

        return payload

    except Exception:
        return None


def get_spotify_login_url():
    """
    Build Spotify's authorization URL.
    """

    settings = get_spotify_settings()

    params = {
        "response_type":
            "code",

        "client_id":
            settings["client_id"],

        "scope":
            SPOTIFY_SCOPES,

        "redirect_uri":
            settings["redirect_uri"],

        "state":
            _create_signed_state(),

        "show_dialog":
            "false",
    }

    return (
        SPOTIFY_AUTHORIZE_URL
        + "?"
        + urlencode(params)
    )


def _post_token_request(form_data):
    """
    Send a token request to Spotify.
    """

    settings = get_spotify_settings()

    credentials = (
        settings["client_id"]
        + ":"
        + settings["client_secret"]
    )

    encoded_credentials = base64.b64encode(
        credentials.encode("utf-8")
    ).decode("utf-8")

    request = Request(
        SPOTIFY_TOKEN_URL,
        data=urlencode(
            form_data
        ).encode("utf-8"),
        headers={
            "Authorization":
                "Basic "
                + encoded_credentials,

            "Content-Type":
                "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    with urlopen(
        request,
        timeout=10,
    ) as response:
        return json.loads(
            response.read()
            .decode("utf-8")
        )


def _save_token_data(token_data):
    """
    Keep the Spotify tokens only in this Streamlit session.
    """

    access_token = token_data.get(
        "access_token"
    )

    if not access_token:
        raise RuntimeError(
            "Spotify did not return an access token."
        )

    expires_in = int(
        token_data.get(
            "expires_in",
            3600,
        )
    )

    st.session_state[
        "spotify_access_token"
    ] = access_token

    # Refresh one minute before the real expiry time.
    st.session_state[
        "spotify_token_expires_at"
    ] = (
        time.time()
        + expires_in
        - 60
    )

    new_refresh_token = token_data.get(
        "refresh_token"
    )

    if new_refresh_token:
        st.session_state[
            "spotify_refresh_token"
        ] = new_refresh_token

    st.session_state[
        "spotify_connected"
    ] = True


def exchange_authorization_code(code):
    """
    Exchange Spotify's temporary code for tokens.
    """

    settings = get_spotify_settings()

    token_data = _post_token_request(
        {
            "grant_type":
                "authorization_code",

            "code":
                code,

            "redirect_uri":
                settings["redirect_uri"],
        }
    )

    _save_token_data(
        token_data
    )

    return token_data


def refresh_spotify_access_token():
    """
    Refresh an expired Spotify access token.
    """

    refresh_token = st.session_state.get(
        "spotify_refresh_token"
    )

    if not refresh_token:
        return None

    token_data = _post_token_request(
        {
            "grant_type":
                "refresh_token",

            "refresh_token":
                refresh_token,
        }
    )

    _save_token_data(
        token_data
    )

    return st.session_state.get(
        "spotify_access_token"
    )


def get_valid_spotify_access_token():
    """
    Return a usable token and refresh it when required.
    """

    access_token = st.session_state.get(
        "spotify_access_token"
    )

    expires_at = st.session_state.get(
        "spotify_token_expires_at",
        0,
    )

    if (
        access_token
        and time.time() < expires_at
    ):
        return access_token

    return refresh_spotify_access_token()


def handle_spotify_callback():
    """
    Process Spotify's redirect back to SoundScope.

    Returns:
        "connected" on success,
        "error" on failure,
        None when this is not a Spotify callback.
    """

    error = st.query_params.get(
        "error"
    )

    if error:
        st.session_state[
            "spotify_auth_error"
        ] = str(error)

        st.query_params.clear()

        return "error"

    code = st.query_params.get(
        "code"
    )

    returned_state = st.query_params.get(
        "state"
    )

    if not code:
        return None

    state_payload = _verify_signed_state(
        returned_state
    )

    if not state_payload:
        st.session_state[
            "spotify_auth_error"
        ] = (
            "Spotify authorization state "
            "could not be verified."
        )

        st.query_params.clear()

        return "error"

    try:
        exchange_authorization_code(
            str(code)
        )

        # Restore the SoundScope login after Spotify's redirect.
        if state_payload.get(
            "user_id"
        ):
            st.session_state[
                "logged_in"
            ] = True

            st.session_state[
                "user_id"
            ] = state_payload.get(
                "user_id"
            )

            st.session_state[
                "username"
            ] = state_payload.get(
                "username"
            )

            st.session_state[
                "role"
            ] = state_payload.get(
                "role",
                "user",
            )

        st.session_state.pop(
            "spotify_auth_error",
            None,
        )

        st.query_params.clear()

        return "connected"

    except Exception as error:
        st.session_state[
            "spotify_auth_error"
        ] = str(error)

        st.query_params.clear()

        return "error"


def spotify_is_connected():
    """
    Check whether Spotify is currently connected.
    """

    return (
        get_valid_spotify_access_token()
        is not None
    )


def disconnect_spotify():
    """
    Remove Spotify tokens from the current session.
    """

    keys = [
        "spotify_connected",
        "spotify_access_token",
        "spotify_refresh_token",
        "spotify_token_expires_at",
        "spotify_auth_error",
    ]

    for key in keys:
        st.session_state.pop(
            key,
            None,
        )
