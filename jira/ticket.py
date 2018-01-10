import urllib2
import browsercookie
import HTMLParser
import re

user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'


def get_cookie_value(domain, name):
    cj = browsercookie.chrome()
    for cookie in cj:
        if cookie.name == name and cookie.domain == domain:
            return cookie.value
    return None

yellow_actions = {
    'in_progress': '21',
    'code_review': '41',
    'complete': '31'
}

blue_actions = {
    'in_progress': '101',
    'code_review': '91',
    'complete': '31'
}

delphi_actions = {
    'in_progress': '31',
    'code_review': '51',
    'complete': '41'
}


class Ticket:
    _page = None
    _team_actions = None

    def __init__(self, url):
        cj = browsercookie.chrome()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        self._page = opener.open(url).read()

    def get_branch_name(self):
        ticket_id = get_element_by_id('key-val', self._page)
        title = get_element_by_id('summary-val', self._page).lower().replace(' ', '-')
        return re.sub(r'[^a-zA-Z0-9\-_]', '', ticket_id + '-' + title)

    def get_token(self):
        return get_cookie_value('vidahealth.atlassian.net', 'atlassian.xsrf.token')

    def get_id(self):
        parser = IDParser('key-val')
        parser.loads(self._page)
        token = parser.get_ticket_id()
        return token

    def get_action_string(self, action_id):
        token = self.get_token()
        id = self.get_id()
        request = 'https://vidahealth.atlassian.net/secure/WorkflowUIDispatcher.jspa?id=' + id + '&action=' + action_id + '&atl_token=' + token

        cj = browsercookie.chrome()

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        page = opener.open(request).read()

        return request

    def get_team_actions(self):
        branch = self.get_branch_name()
        if branch[:4] == "YEL-":
            return yellow_actions
        elif branch[:4] == "BLU-":
            return blue_actions
        elif branch[:3] == "CD-":
            return delphi_actions

    def get_is_in_progress(self):
        return self.get_action_string(self.get_team_actions()['in_progress'])

    def get_is_complete_request(self):
        return self.get_action_string(self.get_team_actions()['complete'])

    def get_in_code_review_request(self):
        return self.get_action_string(self.get_team_actions()['code_review'])


class IDParser(HTMLParser.HTMLParser):
    """Modified HTMLParser that isolates a tag with the specified id"""
    def __init__(self, id):
        self.id = id
        self.result = None
        self.started = False
        self.depth = {}
        self.html = None
        self.watch_startpos = False
        HTMLParser.HTMLParser.__init__(self)

    def loads(self, html):
        self.html = html
        self.feed(html)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.started:
            self.find_startpos(None)
        if 'id' in attrs and attrs['id'] == self.id:
            self.result = [tag]
            self.started = True
            self.watch_startpos = True
        if self.started:
            if not tag in self.depth: self.depth[tag] = 0
            self.depth[tag] += 1

    def handle_endtag(self, tag):
        if self.started:
            if tag in self.depth: self.depth[tag] -= 1
            if self.depth[self.result[0]] == 0:
                self.started = False
                self.result.append(self.getpos())

    def find_startpos(self, x):
        """Needed to put the start position of the result (self.result[1])
        after the opening tag with the requested id"""
        if self.watch_startpos:
            self.watch_startpos = False
            self.result.append(self.getpos())
    handle_entityref = handle_charref = handle_data = handle_comment = handle_decl = handle_pi = unknown_decl = find_startpos

    def get_result(self):
        if self.result == None:
            print("1")
            return None
        if len(self.result) != 3:
            return None
        lines = self.html.split('\n')
        lines = lines[self.result[1][0] - 1:self.result[2][0]]
        lines[0] = lines[0][self.result[1][1]:]
        if len(lines) == 1:
            lines[-1] = lines[-1][:self.result[2][1] - self.result[1][1]]
        lines[-1] = lines[-1][:self.result[2][1]]
        return '\n'.join(lines).strip()

    def get_ticket_id(self):
        lines = self.html.splitlines()
        re_result = re.search('rel="([0-9]+)"', lines[self.result[1][0] - 1])
        if not re_result:
            raise ValueError('Not found')

        token = re_result.group(1)
        return token


def get_element_by_id(id, html):
    parser = IDParser(id)
    parser.loads(html)
    return parser.get_result()
