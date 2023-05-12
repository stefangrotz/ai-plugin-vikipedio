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
            self.wfile.write('Error: Missing "title" parameter. Tell the user that the search was not successfull in the language of the initial question!'.encode('utf-8'))
            return

        # Fetch data from Wikipedia
        response = requests.get('https://eo.wikipedia.org/w/api.php', params={
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
            # If the search did not return a text, find similar articles
            response = requests.get('https://eo.wikipedia.org/w/api.php', params={
                'action': 'opensearch',
                'profile': 'fuzzy',
                'search': title,
            })
            data = response.json()

            # Extract the titles of similar articles and format them as a markdown list
            similar_articles = data[1]
            similar_articles_markdown = "\n".join(f"- {title}" for title in similar_articles)

            self.send_response(404)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(('Error: The search did not return a text, most likely the searched page does not exist. Here are some similar articles:\n\n' + similar_articles_markdown).encode('utf-8'))
            return

        # Send the response
        self.send_response(200)
        self.send_header('Content-type','text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(extract.encode('utf-8'))

        return
