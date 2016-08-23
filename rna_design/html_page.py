import os
import settings

from bs4 import BeautifulSoup
from slimit.parser import Parser


class HTMLPage(object):
    def __init__(self):
        self.head, self.javascript, self.body = "", "", ""

    def add_element(self, element):
        self.head += element.head
        self.javascript += element.javascript
        self.body += element.body

    def to_str(self):
        s = """
        <html>
        <head>
        %s

        <script>
        %s
        </script>
        </head>
        <body>
        %s
        </body>
        </html> """ % (self.head, self.javascript, self.body)

        s = BeautifulSoup(s).prettify()

        return s


class HTMLElement(object):
     def __init__(self):
        self.head, self.javascript, self.body = "", "", ""


class PageRefresher(HTMLElement):
    def __init__(self, refresh_time=120):
        super(PageRefresher, self).__init__()

        self.head += """

        """

class HTMLFileTemplate(HTMLElement):
    def __init__(self, fname):
        super(HTMLFileTemplate, self).__init__()
        self._parse_html_file(fname)

    def _parse_html_file(self, fname):

        if not os.path.isfile(fname):
            fullpath = settings.TEMPLATES_DIR + "/" + fname
            if os.path.isfile(fullpath):
                fname = fullpath

        soup = BeautifulSoup(open(fname))

        #remove javascript, process later
        head = soup.head
        javascripts = []
        if head != None:
            for hidden in head.find_all('script'):
                if len(hidden.text.split('\n')) > 2:
                    javascripts.append(hidden.prettify())
                    hidden.decompose()

            self.head = head.prettify()

        if soup.body != None:
            if len(soup.body.prettify().split('\n')) > 3:
                lines = soup.body.prettify().split('\n')
                lines.pop(0)
                lines.pop()
                self.body = "\n".join(lines)

        self.javascript = ""

        for j in javascripts:
            lines = j.split('\n')
            lines.pop(0)
            lines.pop()
            lines.pop()

            self.javascript += "\n".join(lines)

        try:
            parser = Parser()
            tree = parser.parse(self.javascript)
            self.javascript = tree.to_ecma()
        except:
            raise ValueError("there is an parsing error in the javascript \
                             of this template")



class ProgressBar(HTMLElement):
    def __init__(self, progress=0):
        super(ProgressBar, self).__init__()

        self.body = """<div class="progress">
            <div class="progress-bar progress-bar-striped active"
            role="progressbar" aria-valuenow="%s" aria-valuemin="0"
            aria-valuemax="100" style="width: %s%s"> </div>
       </div> """ % (str(progress), str(progress), "%")

class CanvasJSChart(HTMLElement):
    def __init__(self, ctype="column",data={}, name="Chart1", title={},
                 axisY={}, axisX={}):

        s = """var chart1 = new CanvasJS.Chart(\"%s\",
        {
            %s
        })
        """ % (name, self._print_variables(title, "title"))

        self.javascript = s
        self.body = "<div id=\"%s\" style=\"height: 300px; \
                    width: 100%; \"></div>" % (name)

    def _print_variables(self, var_dict, var_name):
        s = var_name + ": { \n"
        for k,v in var_dict.iteritems():
            s += "\t" + k + ": " + v + ",\n"
        s += "},\n"

