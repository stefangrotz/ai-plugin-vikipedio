from http.server import BaseHTTPRequestHandler
import urllib.parse
import requests

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parse query parameters
        path, _, query_string = self.path.partition('?')
        params = urllib.parse.parse_qs(query_string)
        title = params.get('title', [''])[0]  # Use the 'title' parameter value if it exists, or '' if it doesn't

        if not title:
            # Send an error message if the 'title' parameter is missing
            self.send_response(400)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: Missing "title" parameter. Tell the user that the search was not successfull like this: Die Suche war leider nicht erfolgreich, probiere es bitte noch einmal.'.encode('utf-8'))
            return

        # Fetch data from Wikipedia
        response = requests.get('https://de.wikipedia.org/w/api.php', params={
            'format': 'json',
            'action': 'query',
            'prop': 'extracts',
            'exintro': '1',
            'explaintext': '1',
            'titles': title,
        })
        data = response.json()

        # Extract the page extract text
        pages = data['query']['pages']
        page = next(iter(pages.values()))
        extract = page.get('extract', '')

        if not extract:
            # Send an error message if the search did not return a text
            self.send_response(404)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write('Error: The search did not return a text, most likely the searched page does not exist. Tell the user that the search was not successfull like this: Die Suche war leider nicht erfolgreich, probiere es bitte noch einmal.'.encode('utf-8'))
            return

        # Send the response
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(extract.encode('utf-8'))

        return
