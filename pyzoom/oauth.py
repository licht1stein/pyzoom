import base64
import requests
from pyzoom import err


def make_headers(client_id: str, client_secret: str) -> dict:
    """
    Prepare the payload for a refresh token POST request.

    Parameters:
    data (dict): A dictionary with 'client_id', 'client_secret', and 'refresh-token'.

    Returns:
    dict: A dictionary with 'headers' and 'data' suitable for a POST request.
    """
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    return headers


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
    headers = make_headers(client_id, client_secret)
    data = {"refresh_token": refresh_token, "grant_type": "refresh_token"}
    response = requests.post("https://zoom.us/oauth/token",
                         headers=headers,
                         data=data)

    if response.status_code == 200:
        return response.json()
    raise err.APIError("Failed to refresh tokens")

