## Imports ##

import os
import git


## Constants ##

README_NAMES = ['README', 'readme', 'README.md', 'readme.md']
EXCLUDE_FILES= ['.gitignore', '.gitattributes', '__init__.py'] # Note: do not put README files here!
EXCLUDE_EXTNS= ['*.png'] # Committed file extensions that do not require explanation


## Functions ##

class html_report:
    def __init__(self, outfile, initial_html_text):
        self.text = ""
        self.initial_html_text = initial_html_text
        self.outfile = outfile
        self.layer_no = 0

    def print_layer_start(self):#hit_end_array):
        self.text += "<pre>" + "\t"*self.layer_no
        self.text += "├──"

    def print_layer_end(self):
        self.text += "</pre>"*self.layer_no

    def increment_layer(self):
        self.layer_no += 1

    def decrement_layer(self):
        self.layer_no -= 1

    def finalise_report(self, total_described, total_found):
        init_text = "<h2>README Coverage: {}% </h2>".format(int(100*total_described/total_found))
        init_text += "<h3>Total Found={}, Total Described={}</h3>".format(total_found, total_described)
        self.text = self.initial_html_text + init_text + self.text + "</body></html>"

    #TODO escape this...
    def add_directory(self,dir_name):
        self.text += "<h4 class='direct'>"
        self.print_layer_start()
        self.text += dir_name
        self.print_layer_end()
        self.text += "</h4>"+ "\n"

    def add_included_file(self, file_name):
        self.text += "<h4 class='included_file'>"
        self.print_layer_start()
        self.text += file_name
        self.print_layer_end()
        self.text +=  "</h4>" + "\n"

    def add_excluded_file(self, file_name):
        self.text += "<h4 class='excluded_file'>"
        self.print_layer_start()
        self.text += file_name
        self.print_layer_end()
        self.text += "</h4>" + "\n"


def calc_readme_score(fpath, total_described=0, total_found=0, html=None):
    """
    Recursive function to loop through a file directory to calculate how many files are listed
    and how many are described in the folders' README files. Pass fpath argument to specify the top
    level folder.
    """

    # Get all git-tracked files from this filepath (fpath)
    git_obj = git.cmd.Git(fpath)
    files = [file for file in git_obj.ls_files().split('\n')]
    # Exclude those in subfolders - we'll handle those recursively
    files = [file for file in files if '/' not in file]
    # Do not count files that don't need further explanation
    files = [file for file in files if file not in EXCLUDE_FILES]
    # Remove empty file names
    files = [file for file in files if len(file.strip()) > 0]

    # Remove files with these extenstions ([1:] is to remove the *)
    files = [file for file in files for ext in EXCLUDE_EXTNS if not file.endswith(ext[1:])]

    # Try to find a README file
    my_readme = None
    for readme in README_NAMES:
        if readme in files:
            my_readme = readme
            break

    if my_readme is None:
        total_found += len(files)
        total_described += 0
    else:
        with open(os.path.join(fpath, my_readme), 'r') as f:
            described = f.readlines()

        for file in files:
            # Don't need to describe the README file
            if file == my_readme:
                continue

            total_found += 1
            file_found = False
            for line in described:
                # Must use backticks to properly describe the file
                if '`' + file + '`' in line:
                    file_found = True
                    break

            if file_found:
                total_described += 1
                html.add_included_file(file)
            else:
                html.add_excluded_file(file)

    # Recursive call to each subfolder
    dirs  = [d for d in os.listdir(fpath) if os.path.isdir(os.path.join(fpath, d)) and d != '.git']
    for subfolder in dirs:
        html.add_directory(subfolder)
        html.increment_layer()
        total_described, total_found, html = calc_readme_score(os.path.join(fpath, subfolder), total_described, total_found, verbose, html)

    assert total_found >= total_described
    html.decrement_layer()
    return total_described, total_found, html

if __name__ == "__main__":

    CURRENT_DIRECTORY = os.getcwd()
    INITIAL_HTML_TEXT = """
    <!DOCTYPE html>
        <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Coverage report</title>
    <link rel="stylesheet" href="style.css" type="text/css">

    <script type="text/javascript" src="jquery.min.js"></script>
    <script type="text/javascript" src="jquery.ba-throttle-debounce.min.js"></script>
    <script type="text/javascript" src="jquery.tablesorter.min.js"></script>
    <script type="text/javascript" src="jquery.hotkeys.js"></script>
    <script type="text/javascript" src="coverage_html.js"></script>
    <script type="text/javascript">
        jQuery(document).ready(coverage.index_ready);
    </script>

    <style>
    h3 {color: gray}
    .included_file{color: green;}
    .excluded_file{color: red;}
    .direct {color:  #6666ff;}
    </style>
    </head>
    <body class="indexfile">
    """
    html = html_report(os.path.join("index.html",CURRENT_DIRECTORY),INITIAL_HTML_TEXT)
    fpath = CURRENT_DIRECTORY
    total_described, total_found, html = calc_readme_score(fpath,html=html)
    html.finalise_report(total_described,total_found)

    with open("index.html","w") as file:
        file.write(html.text)
