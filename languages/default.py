# coding: utf8
{
'!langcode!': 'en-us',
'!langname!': 'English (US)',
'%s %%(shop)': '%s %%(shop)',
'%s %%(shop[0])': '%s %%(shop[0])',
'%s %%{quark[0]}': '%s %%{quark[0]}',
'%s %%{shop[0]}': '%s %%{shop[0]}',
'%s %%{shop}': '%s %%{shop}',
'%Y-%m-%d': '%Y-%m-%d',
'%Y-%m-%d %H:%M:%S': '%Y-%m-%d %H:%M:%S',
'@markmin\x01**Hello World**': '**Hello World**',
'About': 'About',
'Access Control': 'Access Control',
'Administrative Interface': 'Administrative Interface',
'Ajax Recipes': 'Ajax Recipes',
'Are you sure you want to delete this object?': 'Are you sure you want to delete this object?',
'Buy this book': 'Buy this book',
'Cannot be empty': 'Cannot be empty',
'Check to delete': 'Check to delete',
'Client IP': 'Client IP',
'Community': 'Community',
'Components and Plugins': 'Components and Plugins',
'Controller': 'Controller',
'Copyright': 'Copyright',
'Created By': 'Created By',
'Created On': 'Created On',
'customize me!': 'customize me!',
'Database': 'Database',
'DB Model': 'DB Model',
'Demo': 'Demo',
'Deployment Recipes': 'Deployment Recipes',
'Description': 'Description',
'Documentation': 'Documentation',
"Don't know what to do?": "Don't know what to do?",
'Download': 'Download',
'E-mail': 'E-mail',
'Email and SMS': 'Email and SMS',
'enter an integer between %(min)g and %(max)g': 'enter an integer between %(min)g and %(max)g',
'enter date and time as %(format)s': 'enter date and time as %(format)s',
'Errors': 'Errors',
'FAQ': 'FAQ',
'First name': 'First name',
'First page #': 'First page #',
'Forms and Validators': 'Forms and Validators',
'Free Applications': 'Free Applications',
'Group %(group_id)s created': 'Group %(group_id)s created',
'Group ID': 'Group ID',
'Group uniquely assigned to user %(id)s': 'Group uniquely assigned to user %(id)s',
'Groups': 'Groups',
'Hello World': 'Hello World',
'Hello World  ## comment': 'Hello World  ',
'Hello World## comment': 'Hello World',
'Home': 'Home',
'How did you get here?': 'How did you get here?',
'Image size': 'Image size',
'Input file': 'Input file',
'Introduction': 'Introduction',
'Invalid email': 'Invalid email',
'Is Active': 'Is Active',
'Last name': 'Last name',
'Layout': 'Layout',
'Layout Plugins': 'Layout Plugins',
'Layouts': 'Layouts',
'Live Chat': 'Live Chat',
'Logged in': 'Logged in',
'Logged out': 'Logged out',
'Login': 'Login',
'Logout': 'Logout',
'Lost Password': 'Lost Password',
'Lost password?': 'Lost password?',
'Margins': 'Margins',
'Menu Model': 'Menu Model',
'Modified By': 'Modified By',
'Modified On': 'Modified On',
'My Sites': 'My Sites',
'Name': 'Name',
'Object or table name': 'Object or table name',
'Online examples': 'Online examples',
'Origin': 'Origin',
'Other Plugins': 'Other Plugins',
'Other Recipes': 'Other Recipes',
'Output format': 'Output format',
'Overview': 'Overview',
'Page size': 'Page size',
'Page width': 'Page width',
'Password': 'Password',
"Password fields don't match": "Password fields don't match",
'pixels': 'pixels',
'please input your password again': 'please input your password again',
'Plugins': 'Plugins',
'Powered by': 'Powered by',
'Preface': 'Preface',
'Profile': 'Profile',
'Python': 'Python',
'Quick Examples': 'Quick Examples',
'Recipes': 'Recipes',
'Record ID': 'Record ID',
'Register': 'Register',
'Registration identifier': 'Registration identifier',
'Registration key': 'Registration key',
'Registration successful': 'Registration successful',
'Remember me (for 30 days)': 'Remember me (for 30 days)',
'Reset Password key': 'Reset Password key',
'Role': 'Role',
'Semantic': 'Semantic',
'Services': 'Services',
'Start': 'Start',
'Stylesheet': 'Stylesheet',
'Support': 'Support',
'The Core': 'The Core',
'The output of the file is a dictionary that was rendered by the view %s': 'The output of the file is a dictionary that was rendered by the view %s',
'The Views': 'The Views',
'This App': 'This App',
'Timestamp': 'Timestamp',
'Twitter': 'Twitter',
'Units': 'Units',
'User %(id)s Logged-in': 'User %(id)s Logged-in',
'User %(id)s Logged-out': 'User %(id)s Logged-out',
'User %(id)s Registered': 'User %(id)s Registered',
'User ID': 'User ID',
'value already in database or empty': 'value already in database or empty',
'Verify Password': 'Verify Password',
'Videos': 'Videos',
'View': 'View',
'Welcome': 'Welcome',
'Welcome to web2py!': 'Welcome to web2py!',
'Which called the function %s located in the file %s': 'Which called the function %s located in the file %s',
'You are successfully running web2py': 'You are successfully running web2py',
'You can modify this application and adapt it to your needs': 'You can modify this application and adapt it to your needs',
'You visited the url %s': 'You visited the url %s',

# Index page
'welcome_page_title': 'Welcome to Family Tree Publisher',
'welcome_page_body': '''\
Family tree publisher is a web application which creates printable or hypertext reports based on family data exported from a 
popular genealogical application [[Agelong Tree http://www.genery.com/]]. Publisher can accept either XML file produced by
``File ▶ Export ▶ XML`` command in Agelong Tree, or ZIP archive containing XML file and images. To produce ZIP file one needs
to export data using the same ``File ▶ Export ▶ XML`` command and make sure that "Export photos" is enabled, then pack all
exported files into a single ZIP file. To produce reports with photos one has to create ZIP file, XML files does not include 
any photos.

Publisher supports two output formats:
- ''OpenDocument'' which is the format understood by OpenOffice or LibreOffice, this format is better suited for printable output 
  and can be edited before printing,
- ''HTML'' which produces single-page document with embedded images, it is obviously better for on-line viewing.
  
Start publisher by uploading your family data (ZIP or XML file) and choosing output format:
''',
'file_validation_failed': 'Error in file',
'welcome_page_footer': '''
Please send me your questions or suggestions using ''Mail'' link at the top of the page. 
''',


# options page
'options_page_title': 'Options for output format',
'options_odt_page_body': '''\
On this page you can change various options controlling the appearance of the produced document. There are options which 
define size of the printed pages, margins, size of the images, and page numbering. By default all sizes are specified in 
inches but you can select your own units (such as centimeters, millimeters, or points).

Note that Table of Contents in produced ODT file will need an update inside LibreOffice or OpenOffice to display all 
entries and page numbers. When you open file in LibreOffice for example, locate and run "Update Indexes and Tables" command
in the menus which should update Table of Contents (located at the end of file).

Check/modify the options and click Start, download window for produced file will open when the file is ready. For large trees 
it may take some time to produce result, do not lose your patience.
''',
'options_html_page_body': '''\
On this page you can change various options controlling the appearance of the produced HTML page. There are options which 
define width of the page and size of the images. All sizes are specified in pixels.

Check/modify the options and click Start, download window for produced file will open when the file is ready. For large trees 
it may take some time to produce result, do not lose your patience.
''',
}
