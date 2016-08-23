import unittest
import rna_design.html_page
import rna_design.settings

from bs4 import BeautifulSoup


class HtmlPageUnittest(unittest.TestCase):

    def test_soup(self):
        f = open(rna_design.settings.TEMPLATES_DIR + "head.html")
        lines = f.readlines()
        f.close()

        s = "".join(lines)
        soup = BeautifulSoup(s)
        # print soup.head.prettify()
        # print soup.body.prettify()

    def test_soup_2(self):

        s = """
          <script>
          </script>

          <script>


            $(document).ready(function () {
                 $("#is_agree").click(function() {
                  if ($(this).is(":checked")) {
                   $("#btn_submit").removeAttr("disabled");
                   $("#btn_demo").removeAttr("disabled");
                   $(this).parent().css("color","black");
                 } else {
                    $("#btn_submit").attr("disabled", "disabled");
                   $("#btn_demo").attr("disabled", "disabled");
                      $(this).parent().css("color","red");
                  }
               </script>
        """

        #soup = BeautifulSoup(s)
        #print soup.find_all('script')[1]

    def test_creation_template(self):
        path = rna_design.settings.TEMPLATES_DIR + "head.html"
        template = rna_design.html_page.HTMLFileTemplate(path)

        template = rna_design.html_page.HTMLFileTemplate("head.html")

    def test_creation_template_extract_js(self):
        path = rna_design.settings.UNITTEST_DIR + "resources/test_head.html"
        template = rna_design.html_page.HTMLFileTemplate(path)

    def test_creation(self):
        path = rna_design.settings.TEMPLATES_DIR + "head.html"
        page = rna_design.html_page.HTMLPage()
        page.add_element(  rna_design.html_page.HTMLFileTemplate(path))

    def test_creation_navbar(self):
        path = rna_design.settings.TEMPLATES_DIR + "navbar.html"
        page = rna_design.html_page.HTMLPage()
        page.add_element(  rna_design.html_page.HTMLFileTemplate(path))

    def test_unittest_head(self):
        path = rna_design.settings.UNITTEST_DIR + "resources/unittest_head.html"
        page = rna_design.html_page.HTMLPage()
        page.add_element( rna_design.html_page.HTMLFileTemplate(path) )
        page.add_element( rna_design.html_page.HTMLFileTemplate("navbar.html"))

        # f = open("test.html", "w")
        # f.write( page.to_str() )
        # f.close()

    def test_progressbar(self):
        path = rna_design.settings.UNITTEST_DIR + "resources/unittest_head.html"
        page = rna_design.html_page.HTMLPage()
        page.add_elemen≡jedi=0, t( rna_desi≡ (*element*) ≡jedi≡gn.html_page.HTMLFileTemplate(path) )
        page.add_element( rna_design.html_page.ProgressBar(50) )

        f = open("test.html", "w")
        f.write( page.to_str() )
        f.close()


def main():
    unittest.main()

if __name__ == '__main__':
    main()
