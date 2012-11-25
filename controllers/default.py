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

import validator


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
    
    form = SQLFORM(db.input_data)
    if form.process(onvalidation=_validateFileForm).accepted:
        
        input_data = db.input_data(form.vars.id)
        logger.debug('input file: %s', input_data)
        
        # save file id in a session and go to options page
        session.input_data_id = form.vars.id
        redirect(URL(options))
        
    return dict(form=form)


def options():
    
    if session.input_data_id is None: redirect(URL(index))
    
    # get 
    input_data = db.input_data(session.input_data_id)
    
    
    options = []
    options += [('Units: ', SELECT('in', 'cm', 'mm', 'pt', _name='units', value=_optval('units', 'in'), _style='width: 80px'))]
    options += [('Page width: ', INPUT(_type='number', _name='page_width', _style='width: 40px', _value='8.5'))]
    if input_data.output_type == 'OpenDocument':
        options += [('Page height: ', INPUT(_type='number', _name='page_height', _style='width: 40px', _value='11'))]

    options += [('Margins: ', 
                 TABLE(TR(INPUT(_type='number', _name='margin_left', _style='width: 30px', _value=_optval('margin_left', '0.5')),
                          DIV(INPUT(_type='number', _name='margin_top', _style='width: 30px', _value='0.5'),
                              BR(),
                              INPUT(_type='number', _name='margin_bottom', _style='width: 30px', _value='0.5')
                              ),
                          INPUT(_type='number', _name='margin_right', _style='width: 30px', _value='0.5'),
                          )))]
    
    options += [(INPUT(_value='Start', _type='submit'), )]
    
    form = FORM(TABLE(*[TR(*opt) for opt in options]))
    
    if form.process().accepted:
        session.options = form.vars
        
    return dict(form=form)


def error():
    return dict()

