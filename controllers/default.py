# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

import os
import logging
import datetime
from StringIO import StringIO
import tempfile

from config import Config 
from drevo_reader import DrevoReader 
from input import FileLocator
import validator
from odt_writer import OdtWriter
from html_writer import HtmlWriter


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

    if not validator.validate(form.vars.input_file.file):
        # if validation fails then display an error
        form.errors.input_file = T('file_validation_failed')
    else:
        # otherwise set hidden fields
        form.vars.original_name = request.vars.input_file.filename
        form.vars.created = datetime.datetime.now()

def index():
    
    form = SQLFORM(db.input_data, submit_button=T("Upload"))
    if form.process(onvalidation=_validateFileForm).accepted:
        
        input_data = db.input_data(form.vars.id)
        logger.debug('input file: %s', input_data)
        
        # save file id in a session and go to options page
        session.input_data_id = form.vars.id
        if form.vars.output_type == 'OpenDocument':
            redirect(URL(options_odt))
        else:
            redirect(URL(options_html))
        
    return dict(form=form)


def options_odt():
    
    if session.input_data_id is None: redirect(URL(index))
    
    # get 
    input_data = db.input_data(session.input_data_id)
    
    options = []
    options += [('Units: ', SELECT('in', 'cm', 'mm', 'pt', _name='units', value=_optval('units', 'in'), _style='width: 80px'))]
    options += [('Page width: ', INPUT(_type='number', _name='page_width', _style='width: 40px', _value=_optval('page_width', '8.5')))]
    options += [('Page height: ', INPUT(_type='number', _name='page_height', _style='width: 40px', _value=_optval('page_height', '11')))]
    options += [('Margins: ', 
                 TABLE(TR(INPUT(_type='number', _name='margin_left', _style='width: 30px', _value=_optval('margin_left', '0.5')),
                          DIV(INPUT(_type='number', _name='margin_top', _style='width: 30px', _value=_optval('margin_top', '0.5')),
                              BR(),
                              INPUT(_type='number', _name='margin_bottom', _style='width: 30px', _value=_optval('margin_bottom', '0.5'))
                              ),
                          INPUT(_type='number', _name='margin_right', _style='width: 30px', _value=_optval('margin_right', '0.5')),
                          )))]
    options += [('First page: ', INPUT(_type='number', _name='first_page', _style='width: 40px', _value=_optval('first_page', '1')))]
    options += [(INPUT(_value='Start', _type='submit'), )]
    
    form = FORM(TABLE(*[TR(*opt) for opt in options]))
    
    if form.process().accepted:
        
        # remember options
        session.options = form.vars
        
        # all config options
        config = Config()
        config['page_width'] = form.vars.page_width+form.vars.units
        config['page_height'] = form.vars.page_height+form.vars.units
        config['margin_left'] = form.vars.margin_left+form.vars.units
        config['margin_top'] = form.vars.margin_top+form.vars.units
        config['margin_bottom'] = form.vars.margin_bottom+form.vars.units
        config['margin_right'] = form.vars.margin_right+form.vars.units
        config['first_page'] = int(form.vars.first_page)

        # convert it
        floc = FileLocator(os.path.join(request.folder, 'uploads', input_data.input_file))
        reader = DrevoReader(floc)

        output = tempfile.TemporaryFile()
        writer = OdtWriter(floc, output, config)
        writer.write(reader)

        # send the file
        output.seek(0)
        response.headers = {'Content-type': 'application/vnd.oasis.opendocument.text'}
        output_name = os.path.splitext(input_data.original_name)[0] + '.odt'
        return response.stream(output, 1048576, attachment=True, filename=output_name)
        
    return dict(form=form)

def options_html():
    
    if session.input_data_id is None: redirect(URL(index))
    
    # get 
    input_data = db.input_data(session.input_data_id)
    
    options = []
    options += [('Units: ', SELECT('in', 'cm', 'mm', 'pt', _name='units', value=_optval('units', 'in'), _style='width: 80px'))]
    options += [('Page width: ', INPUT(_type='number', _name='page_width', _style='width: 40px', _value=_optval('page_width', '8.5')))]
    options += [(INPUT(_value='Start', _type='submit'), )]
    
    form = FORM(TABLE(*[TR(*opt) for opt in options]))
    
    if form.process().accepted:
        
        # remember options
        session.options = form.vars
        
        # all config options
        config = Config()
        config['page_width'] = form.vars.page_width+form.vars.units

        # convert it
        floc = FileLocator(os.path.join(request.folder, 'uploads', input_data.input_file))
        reader = DrevoReader(floc)
        output = tempfile.TemporaryFile()
        writer = HtmlWriter(floc, output, config)        
        writer.write(reader)

        # send the file
        output.seek(0)
        response.headers = {'Content-type': 'text/html'}
        output_name = os.path.splitext(input_data.original_name)[0] + '.html'
        return response.stream(output, 1048576, attachment=True, filename=output_name)
        
    return dict(form=form)


def error():
    return dict()

