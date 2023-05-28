import base64
import requests
from pyzoom import err

import http.server
import webbrowser
from urllib.parse import urlparse, parse_qs, quote

from getpass import getpass


def _make_headers(client_id: str, client_secret: str) -> dict:
    """
    Prepare the headers for an OAuth request to the Zoom API.

    This function accepts client_id and client_secret and returns a dictionary of headers that includes these
    credentials, encoded for HTTP Basic Authentication.

    Parameters:
    client_id (str): The client ID for your Zoom app.
    client_secret (str): The client secret for your Zoom app.

    Returns:
    dict: A dictionary containing the Authorization and Content-Type headers required for an OAuth request.
    """
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    return headers


def _oauth_request(headers, data):
    """
    Send an OAuth token request to the Zoom API.

    This function makes a POST request to the Zoom API's OAuth endpoint, sending the provided headers and data.

    Parameters:
    headers (dict): The headers for the request, including Authorization and Content-Type.
    data (dict): The body of the request, typically including 'grant_type' and a 'refresh_token', 'code', or other parameters.

    Returns:
    dict: The JSON response from the Zoom API, typically containing 'access_token' and 'refresh_token'.

    Raises:
    APIError: If the request does not return a 200 status code, raises an APIError with a message indicating the failure to refresh tokens.
    """
    response = requests.post("https://zoom.us/oauth/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json()
    raise err.APIError("Failed to refresh tokens")


def refresh_tokens(client_id: str, client_secret: str, refresh_token: str):
    """
    Refresh OAuth tokens using client credentials and a refresh token.

    This function makes a request to the Zoom API to refresh the access and refresh tokens.

    Parameters:
    client_id (str): The client ID for your Zoom app.
    client_secret (str): The client secret for your Zoom app.
    refresh_token (str): The current refresh token for the user.

    Returns:
    dict: The JSON response from the Zoom API, typically containing 'access_token' and 'refresh_token'.
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
    client_id (str): The client ID for your Zoom app.
    client_secret (str): The client secret for your Zoom app.
    redirect_uri (str): The redirect URI specified in your Zoom app settings and used in the initial authorization request.
    callback_code (str): The authorization code received in the redirect URI after the user authorized the application.

    Returns:
    dict: The JSON response from the Zoom API, typically containing 'access_token' and 'refresh_token'. These tokens are used
          for accessing and refreshing the user's authorization respectively.
    """
    headers = _make_headers(client_id, client_secret)
    data = {
        "code": callback_code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    return _oauth_request(headers, data)


def oauth_wizard(client_id=None, client_secret=None, port=3000, redirect_uri=None):
    """
    Start a simple HTTP server for capturing the OAuth redirect URI and do everything else to authorize.

    Parameters:
    port (int): The port to start the server on.
    client_id (str): The client ID for your Zoom app.
    redirect_uri (str): The redirect URI specified in your Zoom app settings.

    Returns:
    str: The authorization code captured from the redirect URI.
    """
    if not client_id:
        print("Welcome to interactive pyzoom oauth wizard!\n")
        client_id = getpass("Client ID: ")

    if not client_secret:
        client_secret = getpass("Client Secret: ")

    class RequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()

            query = urlparse(self.path).query
            params = parse_qs(query)
            if "code" in params:
                self.server.authorization_code = params["code"][0]

            self.wfile.write(b"You can close this page.")

    redirect_uri = redirect_uri or f"http://localhost:{port}/integrations/zoom"
    redirect_uri_encoded = quote(redirect_uri, safe="")
    server_address = ("", port)

    url = f"https://zoom.us/oauth/authorize?response_type=code&client_id={quote(client_id)}&redirect_uri={redirect_uri_encoded}"
    input(
        f"Press enter to start a callback server and open Zoom oauth page in your default browser..."
    )
    webbrowser.open(url)

    print(f"Starting callback server on {redirect_uri}")
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    httpd.handle_request()

    code = httpd.authorization_code
    if not client_secret:
        return code

    result = request_tokens(client_id, client_secret, redirect_uri, code)
    print(result)
    return result


if __name__ == "__main__":
    oauth_wizard()
