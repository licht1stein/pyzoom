import base64
import requests
from pyzoom import err


def _make_headers(client_id: str, client_secret: str) -> dict:
    """
    Prepare the payload for a refresh token POST request.

    Parameters:
    data (dict): A dictionary with 'client_id', 'client_secret', and 'refresh-token'.

    Returns:
    dict: A dictionary with 'headers' and 'data' suitable for a POST request.
    """
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    return headers


def _oauth_request(headers, data):
    response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    raise err.APIError("Failed to refresh tokens")


def refresh_tokens(client_id: str, client_secret: str, refresh_token: str):
    """
    Refresh OAuth tokens using client credentials and a refresh token.

    Parameters:
    client_id (str): The client ID for the authorization.
    client_secret (str): The client secret for the authorization.
    refresh_token (str): The refresh token for obtaining new tokens.

    Returns:
    Response: The response from the token refresh request.
    """
    headers = _make_headers(client_id, client_secret)
    data = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
    return _oauth_request(headers, data)


def request_tokens(client_id, client_secret, redirect_uri, callback_code):
    """
    Request OAuth tokens from the Zoom API using client credentials, a redirect URI, and a callback code.

    This function is part of the OAuth 2.0 authorization flow specific to the Zoom API. After the user
    has authorized the application, they will be redirected to a specified redirect URI, along with a
    callback code. This function uses that code, along with the client ID, client secret, and the same
    redirect URI, to request access and refresh tokens from the Zoom API.

    Parameters:
    client_id (str): The client ID for the application, obtained from your Zoom App Dashboard.
    client_secret (str): The client secret for the application, also obtained from your Zoom App Dashboard.
    redirect_uri (str): The redirect URI specified in the initial authorization request and registered in the Zoom App Dashboard.
    callback_code (str): The authorization code received as a query parameter in the redirect from the Zoom API.

    Returns:
    Response: The response from the Zoom API, typically containing access and refresh tokens in the JSON body.
    """
    headers = _make_headers(client_id, client_secret)
    data = {
        "code": callback_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    return _oauth_request(headers, data)
