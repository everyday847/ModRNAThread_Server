 pdb_img = DATA_BASE_DIR + data_dir + "/rna.png"
    shutil.copy(pdb_img, "res/images")



    s = get_html_head()
    s += "<meta http-equiv=\"refresh\" content=\"120\">"
    s += """
    <script>
     setInterval(function() {
                  window.location.reload();
                }, 120000);
    </script>
    """
    s += "</head><body>"
    s += get_nav_bar()
    s +=  """

       <div class="container">
        <h1>Job Status: Queued</h1>

       <div class="progress">
            <div class="progress-bar progress-bar-striped active" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%">
           </div>
       </div>
       <table>
       <tr>
       <td style=\"width: 70%; vertical-align: top;
  text-align: left;}\">
        blah<br>
        blah
        blah
        blah
       </td>
       <td style=\"text-align: right"\">
       <img src= \"/res/images/rna.png\" style=\"
       max-height: 150%; width: 250%\" />
       </td>
       </tr>
       </table>
       </div>


        </body>
        </html>"""

