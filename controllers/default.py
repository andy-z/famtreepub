# -*- coding: utf-8 -*-
# ## required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request, db)
def call(): return service()
# ## end requires

import os
import logging
import datetime
import tempfile
import traceback

import ftp_config
from drevo_reader import DrevoReader
from input import FileLocator
import validator
from odt_writer import OdtWriter
from html_writer import HtmlWriter

_log = logging.getLogger("web2py.app.famtreepub")
_log.setLevel(logging.DEBUG)

def _optval(name, defval):
    '''Get option value from a session or use default if session does not have it.'''
    val = request.vars[name]
    if val is not None: return val
    val = session['options']
    if val is None: return defval
    val = val[name]
    if val is None: val = defval
    return val

def _validateFileForm(form):
    '''Validate file passed to the file foram'''

    # at this point form data are not on disk yet, and form contains complete
    # file data, not a file name.

    input_data = db.input_data(form.vars.id)
    _log.info('index: input file: %s', input_data)
    try:
        validator.validate(os.path.join(request.folder, 'uploads', input_data.input_file))
        # on success set hidden fields
        input_data.update_record(original_name=request.vars.input_file.filename, created=datetime.datetime.now())
        _log.info('index: validation succeeded')
        return True
    except Exception as ex:
        # if validation fails then display an error
        form.errors.input_file = T('file_validation_failed') + ': ' + str(ex)
        _log.info('index: validation failed', exc_info=True)
        return False


def index():
    """Landing page.

    Shows upload form for an input file.
    """
    form = SQLFORM(db.input_data, submit_button=T("Upload"))
    if form.process(onsuccess=None).accepted:

        if _validateFileForm(form):

            # save file id in a session and go to options page
            session.input_data_id = form.vars.id
            if form.vars.output_type == 'OpenDocument':
                redirect(URL(options_odt))
            else:
                redirect(URL(options_html))

    return dict(form=form)


def options_odt():
    """OpenDocument options page.

    Shows bunch of options for conversion to ODT format. Converts to ODF
    using those options.
    """
    if session.input_data_id is None: redirect(URL(index))

    # get
    input_data = db.input_data(session.input_data_id)

    options = []
    options += [(T('Units') + ': ', SELECT('in', 'cm', 'mm', 'pt', _name='units', value=_optval('units', 'in'), _style='width: 80px'))]
    options += [(T('Page size') + ': ',
                 INPUT(_type='text', _name='page_width', _style='width: 40px', _value=_optval('page_width', '6')) +
                 ' x ' +
                 INPUT(_type='text', _name='page_height', _style='width: 40px', _value=_optval('page_height', '9'))
                 )]
    options += [(T('Margins') + ': ',
                 TABLE(TR(INPUT(_type='text', _name='margin_left', _style='width: 30px', _value=_optval('margin_left', '0.5')),
                          DIV(INPUT(_type='text', _name='margin_top', _style='width: 30px', _value=_optval('margin_top', '0.5')),
                              BR(),
                              INPUT(_type='text', _name='margin_bottom', _style='width: 30px', _value=_optval('margin_bottom', '0.25'))
                              ),
                          INPUT(_type='text', _name='margin_right', _style='width: 30px', _value=_optval('margin_right', '0.5')),
                          ))
                 )]
    options += [(T('Image size') + ': ',
                 INPUT(_type='text', _name='image_width', _style='width: 40px', _value=_optval('image_width', '2.5')) +
                 ' x ' +
                 INPUT(_type='text', _name='image_height', _style='width: 40px', _value=_optval('image_height', '2.5'))
                 )]
    options += [(T('First page #') + ': ', INPUT(_type='number', _name='first_page', _style='width: 50px', _value=_optval('first_page', '1')))]
    fmtoptions = [OPTION(T('31.12.2001'), _value='DMY.'),
                  OPTION(T('31/12/2001'), _value='DMY/'),
                  OPTION(T('2001-12-31'), _value='YMD-'),
                  OPTION(T('12/31/2012'), _value='MDY/')]
    options += [(T('Date format') + ': ', SELECT(*fmtoptions, _name='datefmt', value=_optval('datefmt', 'DMY.'), _style='width: 150px'))]
    options += [('', INPUT(_value=T('Start'), _type='submit'),)]

    form = FORM(TABLE(*[TR(*[TD(o) for o in opt]) for opt in options]))

    if form.process().accepted:

        # remember options
        session.options = form.vars

        # all config options
        config = ftp_config.Config()
        config['page_width'] = form.vars.page_width + form.vars.units
        config['page_height'] = form.vars.page_height + form.vars.units
        config['margin_left'] = form.vars.margin_left + form.vars.units
        config['margin_top'] = form.vars.margin_top + form.vars.units
        config['margin_bottom'] = form.vars.margin_bottom + form.vars.units
        config['margin_right'] = form.vars.margin_right + form.vars.units
        config['image_width'] = form.vars.image_width + form.vars.units
        config['image_height'] = form.vars.image_height + form.vars.units
        config['first_page'] = int(form.vars.first_page)
        config['date_format'] = form.vars.datefmt

        # convert it
        floc = FileLocator(os.path.join(request.folder, 'uploads', input_data.input_file))
        reader = DrevoReader(floc)

        output = tempfile.TemporaryFile()
        writer = OdtWriter(floc, output, config)
        writer.write(reader)

        # send the file
        output.seek(0)
        response.headers['Content-Type'] = 'application/vnd.oasis.opendocument.text'
        output_name = os.path.splitext(input_data.original_name)[0] + '.odt'
        return response.stream(output, 1048576, attachment=True, filename=output_name)

    return dict(form=form)

def options_html():
    """HTML options page.

    Shows bunch of options for conversion to HTML format. Converts to HTML
    using those options.
    """
    if session.input_data_id is None: redirect(URL(index))

    # get
    input_data = db.input_data(session.input_data_id)

    options = []
    options += [(T('Page width') + ': ', INPUT(_type='number', _name='html_page_width', _style='width: 50px', _value=_optval('html_page_width', '800')) +
                 ' ' + T('pixels'))]
    options += [(T('Image size') + ': ',
                 INPUT(_type='number', _name='html_image_width', _style='width: 50px', _value=_optval('html_image_width', '300')) +
                 ' x ' +
                 INPUT(_type='number', _name='html_image_height', _style='width: 50px', _value=_optval('html_image_height', '300')) +
                 ' ' + T('pixels'))]

    checked = _optval('html_image_upscale', '') == 'checked'
    options += [(T('Upscale images') + ': ',
               INPUT(_type='checkbox', _name='html_image_upscale', _value='checked', value=checked))]

    fmtoptions = [OPTION(T('31.12.2001'), _value='DMY.'),
                  OPTION(T('31/12/2001'), _value='DMY/'),
                  OPTION(T('2001-12-31'), _value='YMD-'),
                  OPTION(T('12/31/2012'), _value='MDY/')]
    options += [(T('Date format') + ': ', SELECT(*fmtoptions, _name='datefmt', value=_optval('datefmt', 'DMY.'), _style='width: 150px'))]

    options += [('', INPUT(_value=T('Start'), _type='submit'))]

    form = FORM(TABLE(*[TR(*[TD(o) for o in opt]) for opt in options]))

    if form.process().accepted:

        # remember options
        session.options = form.vars

        # all config options
        config = ftp_config.Config()
        config['page_width'] = form.vars.html_page_width + 'px'
        config['image_width'] = form.vars.html_image_width + 'px'
        config['image_height'] = form.vars.html_image_height + 'px'
        config['image_upscale'] = form.vars.html_image_upscale == 'checked'
        config['date_format'] = form.vars.datefmt

        # convert it
        floc = FileLocator(os.path.join(request.folder, 'uploads', input_data.input_file))
        reader = DrevoReader(floc)
        output = tempfile.TemporaryFile()
        writer = HtmlWriter(floc, output, config)
        writer.write(reader)

        # send the file
        output.seek(0)
        response.headers['Content-Type'] = 'text/html'
        output_name = os.path.splitext(input_data.original_name)[0] + '.html'
        return response.stream(output, 1048576, attachment=True, filename=output_name)

    return dict(form=form)


def language():
    """Set preferred language.

    Get language code from a request variable and remembers it in a session.
    The code in models/lang module uses this session variable to change
    translation language. Redirects back to the referrer page.
    """
    session.ui_lang = request.vars['lang']
    if request.env.http_referer:
        redirect(request.env.http_referer)
    else:
        redirect(URL(index))

def error():
    return dict()

