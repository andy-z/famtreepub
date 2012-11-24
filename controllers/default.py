# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call(): return service()
### end requires

def _optval(name, defval):
    '''Get option value from a session or use default if session does not have it.'''
    val = session['options']
    if val is None: return defval
    val = val[name]
    if val is None: val = defval
    return val

def index():
    
    form = SQLFORM(db.input_data)
    if form.process().accepted:
        
        # verify that file contents is acceptable
        
        # save file id in a session and go to options page 
        redirect(URL('options', vars=dict(input_data_id=form.vars.id)))
        
    return dict(form=form)


def options():
    
    # get 
    input_data = db.input_data(request.vars.input_data_id)
    
    form = FORM(TABLE(
                      TR('Units: ', SELECT('in', 'cm', 'mm', 'pt', _name='units', _value=_optval('units', 'in'), _style='width: 80px'), '', ''),
                      TR('Page width: ', INPUT(_type='number', _name='page_width', _style='width: 40px', _value=_optval('page_width', '8.5')),
                         TD('Margins: ', _rowspan=2),
                         TD(TABLE(TR(
                                  INPUT(_type='number', _name='margin_left', _style='width: 30px', _value=_optval('margin_left', '0.5')),
                                  DIV(
                                      INPUT(_type='number', _name='margin_top', _style='width: 30px', _value='0.5'),
                                      BR(),
                                      INPUT(_type='number', _name='margin_bottom', _style='width: 30px', _value='0.5')
                                      ),
                                  INPUT(_type='number', _name='margin_right', _style='width: 30px', _value='0.5'),
                                  )), _rowspan=2)
                         ),
                      TR('Page height: ', INPUT(_type='number', _name='page_height', _style='width: 40px', _value='11')),
                      TR('', INPUT(_value='Start', _type='submit'))
                      )
                )
    
    if form.process().accepted:
        session['options'] = form.vars
        
    return dict(form=form)


def error():
    return dict()

