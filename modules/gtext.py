# -*- coding: utf-8 -*-
'''
Created on Sep 8, 2012

@author: salnikov
'''

def gtext(str, person = None):
    if str == 'Unknown': return u'Неизвестно'
    if str == 'Born' and person.sex == 'M': return u'Родился'
    if str == 'Born' and person.sex == 'F': return u'Родилась'
    if str == 'Died' and person.sex == 'M': return u'Умер'
    if str == 'Died' and person.sex == 'F': return u'Умерла'
    if str == 'Mother': return u'Мать'
    if str == 'Father': return u'Отец'
    if str == 'Spouse' and person.sex == 'M': return u'Супруга'
    if str == 'Spouse' and person.sex == 'F': return u'Супруг'
    if str == 'kid' and person.sex == 'M': return u'сын'
    if str == 'kid' and person.sex == 'F': return u'дочь'
    if str == 'kids': return u'дети'
    if str == 'Kids': return u'Дети'
    if str == 'Marriage': return u'Свадьба'
    if str == 'Spouses and children': return u'Супруги и дети'
    if str == 'Events and dates': return u'События и даты'
    if str == 'Ancestor tree': return u'Предки'
    if str == 'Comments': return u'Комментарии'
    if str == 'Person List': return u'Персоналии'
    if str == 'Statistics': return u'Статистика'
    if str == 'Total Statistics': return u'Общая статистика'
    if str == 'Name Statistics': return u'Статистика имен'
    if str == 'Female Name Frequency': return u'Частота женских имен'
    if str == 'Male Name Frequency': return u'Частота мужских имен'
    if str == 'Table Of Contents': return u'Оглавление'
    return str
