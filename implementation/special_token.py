import re

def special_token(text_list, prefix_words):
    special_tokens =[]
    #add special_tokens
    for index in range(len(text_list)):
        dates, text_list[index] = sub_date(text_list[index]) # return a list of date and the text
        others, text_list[index] = store_rest(text_list[index])
        text_list[index] = sub_digit(text_list[index]) # substitute digits
        mones, text_list[index] = monetary(text_list[index])# return a list of monetary values and the text
        text_list[index] = sub_abbreviations(text_list[index])
        hyphs, text_list[index] = sub_hyph(text_list[index], prefix_words) # return a list of 3+ alphs and the text 
        
        to_add = hyphs + mones + dates + others
        add_special_token(to_add, special_tokens)
    
    return special_tokens, text_list

def add_special_token(list, s_tokens):
    if list == []:
        return s_tokens

    for word in list:
        s_tokens.append(word)
    return s_tokens

def sub_abbreviations(text):
    abbre = re.match('[A-Za-z]+\.+[A-Z\.a-z]*', text)
    if not abbre:
        return text
    word = re.sub('\.', '', abbre.group(0))
    return word.lower()

def sub_hyph(text, prefix_words):
    all_hyph = re.match('[A-Za-z0-9]+(-[A-Za-z0-9]+){1,3}', text)
    no_hyphs = []
    if not all_hyph:
        return [], text
    three_alphs = re.findall('[A-Za-z]{3,}', all_hyph.group(0))
    for part in three_alphs:
        if part in prefix_words:
            three_alphs.remove(part)
    remove_hyph = re.sub('-', '', all_hyph.group(0))
    no_hyphs.append(remove_hyph)
    no_hyphs += three_alphs
    return no_hyphs, ''

def monetary(text):
    all_monetary = re.match('^\$[0-9,]+\.?[0-9]*$', text)
    if not all_monetary:
        return [], text
    text = re.sub(',', '', all_monetary.group(0))
    text = re.sub('\.0{1,}', '', text)
    text = re.sub('\.', '', text)
    return [text], ''

def date_with_space(text):
    # before tokenizing
    dates = re.finditer('(January|Jan|February|Feb|March|Mar|April|Apr|May|June|Jun|July|Jul|August|Aug|September|Sep|October|Oct|November|Nov|December|Dec)\.?\s+(0?[1-9]|[12][0-9]|[3][01]),\s+([1-2][0-9][0-9][0-9]|[1-9][0-9][0-9]|[0-9][0-9])', text)
    for d in dates:
        date_split = d.group(0).split()
        date_split[0] = date_split[0][:3]
        date_split[1] = date_split[1][:-1]
        subd_date = date_split[0] + '-' + date_split[1] + '-' + date_split[2]
        text = re.sub(d.group(0), subd_date, text)
    return text

def sub_date(text):
    # return a list of sub date and the text
    all_date = re.match('^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|0?[1-9]|1[0-2])[-/](0?[1-9]|[12][0-9]|[3][01])[-/]([1-2][0-9][0-9][0-9]|[1-9][0-9][0-9]|[0-9][0-9])', text)
    if not all_date:
        return [], text
    text_split = re.split('\W', all_date.group(0))
    months = {'Jan': '01', 'Feb':'02', 'Mar' : '03', 'Apr' : '04', 'May' : '05', 'Jun' : '06', 'Jul' : '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12' }
    if len(text_split[0]) > 2:
        month = months[text_split[0]]
    elif len(text_split[0]) == 1:
        month = '0' + text_split[0]
    else:
        month = text_split[0]
    
    if len(text_split[1]) == 1:
        day = '0' + text_split[1]
    else:
        day = text_split[1]
    
    if len(text_split[2]) == 2:
        year_int = int(text_split[2])
        if year_int <= 20:
            year = '20' + text_split[2]
        else:
            year = '19' + text_split[2]
    else:
        year = text_split[2]

    date = month + '-' + day + '-' + year
    return [date], ''

def sub_digit(text):
    #only sub digit with no special token returning
    digit_with_comma = re.match('\d+[,\d+]\.?\d*', text)
    if digit_with_comma:
        text = re.sub(',', '', digit_with_comma.group(0))
    end_zero_digit = re.match('[0-9,]*\.0{1,}', text)
    if end_zero_digit:
        text = re.sub('\.0{1,}', '', end_zero_digit.group(0))
    return text

def store_rest(text):
    #file extensions
    file_ext = re.match('^[\w\-\.]+\.[\w]+$', text)
    #email
    email = re.match('^[\w\._\%\+\-]+@[\w]+([\.\-_]?[\w]+)+\.[\w]+$', text)
    #IP address
    ip = re.match('^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])(\.25[0-5]|\.2[0-4][0-9]|\.1[0-9][0-9]|\.[1-9]?[0-9]){3,}$', text)
    #URLs
    url = re.match('^https?:\/\/[^\s\$\.?\#].[^\s]*$', text)
    if not(file_ext or email or ip or url):
        return [], text
    if ip:
        text = ip.group(0)
        
    elif url:
        text = url.group(0)
        
    elif email:
        text = email.group(0)
    elif file_ext:
        extd = re.split('\.', file_ext.group(0))[-1]
        text = re.sub('\.', '', file_ext.group(0))
        return [extd, text], ''
    return [text], ''
