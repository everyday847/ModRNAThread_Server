import cherrypy
from cherrypy.lib.static import serve_file

import os
import random
import string
import sys
import shutil
import subprocess
import time

import rna_design.html_page

MEDIA_DIR = os.path.join(os.path.abspath("."))
DATA_BASE_DIR = MEDIA_DIR + "/data/"

class BasePage(rna_design.html_page.HTMLPage):
    def __init__(self):
       super(BasePage, self).__init__()
       self.add_element ( rna_design.html_page.HTMLFileTemplate("head.html") )
       self.add_element ( rna_design.html_page.HTMLFileTemplate("navbar.html") )


class ResultsWaitingPage(BasePage):
    def __init(self):
       super(ResultsWaitingPage, self).__init__()

    def _get_job_pos(self, data_dir):
        f = open(MEDIA_DIR + '/jobs.dat')
        lines = f.readlines()
        f.close()

        for i, l in enumerate(lines):
            if data_dir in l:
                return i

    def _remove_job(self, data_dir):
        f = open(MEDIA_DIR + '/jobs.dat')
        lines = f.readlines()
        f.close()

        f = open(MEDIA_DIR + '/jobs.dat', 'w')
        for l in lines:
            if data_dir in l:
                continue
            f.write(l)

        f.close()

    def _progress_bar_status(self, data_dir):
        path = DATA_BASE_DIR + data_dir + "/rna.pdb"
        if not os.path.isfile(path):
            job_pos = self._get_job_pos(data_dir)
            return ["Queued, "+str(job_pos) + " jobs ahead", 0]

        path = DATA_BASE_DIR + data_dir + "/threaded.pdb"
        if not os.path.isfile(path):
            return ["Running", 50]

        path = DATA_BASE_DIR + data_dir + "/svr.png"
        if not os.path.isfile(path):
            return ["Plotting Results", 80]

        return ["Generating Results Page", 90]

    def _is_pdb_valid(self, data_dir):
        os.chdir(DATA_BASE_DIR + data_dir)
        #subprocess.call("make_rna_rosetta_ready.py -remove_ions rna.pdb",
        #                shell=True)

        # This seems to be interested in how many residues there are
        # we aren't.
        return True
        
    def render(self, data_dir):
        try:
            status, percent = self._progress_bar_status(data_dir)
        except:
            status, percent = "Generating Results Page", 90

        if percent == -1:
            f = open(DATA_BASE_DIR+data_dir+'/ERROR', 'w')
            f.write(status+"\n")
            f.close()

        if os.path.isfile(DATA_BASE_DIR+data_dir+'/ERROR'):
            percent = -1
            f = open(DATA_BASE_DIR+data_dir+'/ERROR')
            lines = f.readlines()
            f.close()
            status = lines[0]

        if percent == -1:
            self._remove_job(data_dir)
            title = "<H1>"+status+"</H1>"
            progress_bar =  rna_design.html_page.HTMLPage()
        else:
            title = "<H1> Job Status: %s</H1>" % (status)
            progress_bar =  rna_design.html_page.ProgressBar(percent)
        waiting_table = ""

        body = """
        <div class="container">
        %s
        %s
        %s
        </div>
        """ % (title, progress_bar.body, waiting_table)

        self.body += body
        self.javascript += """
                setTimeout(function(){
                window.location.reload(1);
                 }, 60000);
        """

        return percent


def is_valid_name(input, char_allow, length):

    if len(input) <= length: return False
    src = ''.join([string.digits, string.ascii_letters, char_allow])
    for char in input:
        if char not in src: return False
    return True


def is_valid_email(input):

    input_split = input.split("@")
    if len(input_split) != 2: return False
    if not is_valid_name(input_split[0], ".-_", 2): return False
    input_split = input_split[1].split(".")
    if len(input_split) == 1: return False
    for char in input_split:
        if not is_valid_name(char, "", 1): return False
    return True

def format_pdb_num(num):
    s = "S_"

    if num < 1000:
        s += "0"
    if num < 100:
        s += "0"
    if num < 10:
        s += "0"
    s += str(num)
    return s + ".pdb"

def get_nav_bar():
    return """<div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="/res/html/Design.html">&nbsp;&nbsp;ModRNAThread&nbsp;&nbsp;</a>

        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="/res/html/Design.html">Home</a></li>
            <li><a href="/res/html/Tutorial.html">Tutorial</a></li>
            <li><a href="/res/html/About.html">About</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </div>
    """


def get_html_head():
    return """<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="description" content="">
        <meta name="author" content="">
        <link rel="shortcut icon" href="/images/EteRNA_shortcut.png">
        <title>ModRNAThread Server</title>

        <!-- Bootstrap core CSS -->
        <link href="/res/css/bootstrap.min.css" rel="stylesheet">
        <!-- Bootstrap theme -->
        <link href="/res/css/bootstrap-theme.min.css" rel="stylesheet">
        <!-- Custom styles for this template -->
        <link href="/res/css/theme.css" rel="stylesheet">
        <!-- Latest compiled and minified JavaScript -->
        <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
        <script src="/res/js/bootstrap.min.js"></script>
        <script src="/res/js/canvasjs.min.js"></script>
    """


class rest:

    @cherrypy.expose
    def index(self):
        return open(os.path.join(MEDIA_DIR, u"res/html/Design.html"))

    @cherrypy.expose
    def thread_rna(self, pdb_file, nstruct, sequence="", format="DEFAULT", mutation_list="", insertion_list="",email=""):
        job_dir = os.urandom(16).encode('hex')
        new_dir = "data/"+job_dir
        os.mkdir(new_dir)

        f = open(new_dir + "/rna.pdb", "w")
        while True:
            data = pdb_file.file.read(8192)
            f.write(data)
            if not data:
                break

        f.close()

        f = open("jobs.dat","a")
        f.write(new_dir + " | " + nstruct + " | " + sequence + " | " + format + " | " + mutation_list + " | " + insertion_list + " | " + email + "\n")
        f.close()

        raise cherrypy.HTTPRedirect('/result/' + job_dir)

    @cherrypy.expose
    def result(self, dir_id):
        # job not done show waiting page
        path = DATA_BASE_DIR + dir_id + "/cluster_1.png"
        error = DATA_BASE_DIR + dir_id + "/ERROR"
        if not os.path.isfile(path) or os.path.isfile(error):
            page = ResultsWaitingPage()
            percent = page.render(dir_id)
            return page.to_str()

        # job is done show results
        all_path =  DATA_BASE_DIR + dir_id + "/all.zip"

        RMSD_file = "data/" + dir_id + "/score.sc"
        score_file = "data/" + dir_id + "/score.sc"

        s = get_html_head()
        s += "</head>"
        s += "<body>\n"
        s += get_nav_bar()
        s += "<center><H2>Job "+dir_id + " Results </H2></center>"
        s += """<div class=\"starter-template\">
         <div class=\"container theme-showcase\" role=\"main\">"""

        #s += "<a href=/download/?filepath=%s><button type=\"button\" \
        #      class=\"btn btn-primary\">Download Everything</button></a>" % (all_path)
        s += "<a href=/download/?dir_id=%s&data=all><button type=\"button\" \
              class=\"btn btn-primary\">Download Everything</button></a>" % (dir_id)
        s += "<br><br><br>"

        s += "<br /><br />"
        s += "<table><tr><th colspan='3'><center><h3>Top three clusters</h3></center></th></tr>"
        s += "<tr><td><img src=/data/"+dir_id+"/cluster_1.png /></td>"
        s += "<td><img src=/data/"+dir_id+"/cluster_2.png /></td>"
        s += "<td><img src=/data/"+dir_id+"/cluster_3.png /></td></tr>"
        s += "<tr><th colspan='3'><center><h3>Score vs. RMSD</h3></center></th></tr>"
        s += "<tr><td colspan='3'><img src=/data/"+dir_id+"/svr.png /></tr></tr>"
        s += "</table></body></html>"

        return s


class Download:

    def index(self, dir_id, data):
        filepath =  DATA_BASE_DIR + dir_id + "/all.zip"
        return serve_file(filepath, "application/x-download", "attachment")
    index.exposed = True


if __name__ == "__main__":
    server_state = "development"
    if len(sys.argv) > 1:
        server_state = sys.argv[1]
    if server_state not in ("development","release"):
        raise SystemError("ERROR: Only can do development or release")
    if server_state == "development":
        socket_host = "127.0.0.1"
        socket_port = 3030
    else:
        socket_host = "0.0.0.0"
        #socket_host = "52.10.248.184"
        socket_port = 8080

    cherrypy.config.update( {
        "server.socket_host":socket_host,
        "server.socket_port":socket_port,
        "tools.staticdir.root": os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
    } )
    root = rest()
    root.download = Download()

    if server_state == "development":
        cherrypy.quickstart(root, "", "test.conf")
    else:
        cherrypy.quickstart(root, "", "app.conf")


