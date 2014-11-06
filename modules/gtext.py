# -*- coding: utf-8 -*-
'''
Created on Sep 8, 2012

@author: salnikov
'''

def gtext(txt, person=None):
    if txt == 'Unknown': return u'Неизвестно'
    if txt == 'Born':
        if person.sex == 'F': return u'Родилась'
        return u'Родился'
    if txt == 'Died':
        if person.sex == 'F': return u'Умерла'
        return u'Умер'
    if txt == 'Mother': return u'Мать'
    if txt == 'Father': return u'Отец'
    if txt == 'Spouse':
        if person.sex == 'M': return u'Супруга'
        return u'Супруг'
    if txt == 'kid':
        if person.sex == 'M': return u'сын'
        if person.sex == 'F': return u'дочь'
        return ''
    if txt == 'kids': return u'дети'
    if txt == 'Kids': return u'Дети'
    if txt == 'Marriage': return u'Свадьба'
    if txt == 'Spouses and children': return u'Супруги и дети'
    if txt == 'Events and dates': return u'События и даты'
    if txt == 'Ancestor tree': return u'Предки'
    if txt == 'Comments': return u'Комментарии'
    if txt == 'Person List': return u'Персоналии'
    if txt == 'Statistics': return u'Статистика'
    if txt == 'Total Statistics': return u'Общая статистика'
    if txt == 'Name Statistics': return u'Статистика имен'
    if txt == 'Female Name Frequency': return u'Частота женских имен'
    if txt == 'Male Name Frequency': return u'Частота мужских имен'
    if txt == 'Table Of Contents': return u'Оглавление'
    if txt == 'Person count': return u'Всего персон'
    if txt == 'Female count': return u'Женского пола'
    if txt == 'Male count': return u'Мужского пола'
    return txt
