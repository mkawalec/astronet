from flask import Response

from ..database import db_session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import state


def gen_filename(length=12):
    """ Generates a (rougly) random string of a given length
        consisting of upper and lower case letters and numbers.
        
        The default works well for situations when a reasonable 
        entropy is needed (filenames?)
    """
    filename = []
    chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
             'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'w', 'x',
             'y', 'q', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
             'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'R', 'S', 'T',
             'U', 'W', 'Q', 'X', 'Y', 'Z', '1', '2', '3', '4', '5',
             '6', '7', '8', '9', '0']
    
    for i in range(length):
        filename.append(chars[randint(0, len(chars)-1)])
    return ''.join(filename)

## Sends to the client a StringIO object not analysing
## its contents in any way - it will be base64
## encoded before sending
def send_base64(what):
    """ Base64 encodes a file and sends it in http request """
    what.seek(0)
    ret = b64encode(what.getvalue())
    
    headers = {}
    headers['Content-Type'] = 'application/base64'
    
    return Response(ret,headers=headers, mimetype='application/base64', 
            direct_passthrough=True, status='200 OK')



def create_query(feed):
    """ Creates a full-text query from user-provided text data in *feed* """
    words = feed.strip().split()
    
    query = ''
    for (i,word) in enumerate(words):
        if '|' in word:
            # We don't want weird words
            continue
        if len(word) > 2:
            if i != 0 and len(query) > 0:
                query += ' | '
            query += word
    return query

def stringify(results, one=False):
    """ Encode all of the results as strings to get rid of non-matching
        datatypes issues
    """
    if one:
        for param in results:
            results[param] = unicode(results[param])
        return results

    for result in results:
        for param in result:
            result[param] = unicode(result[param])

    return results

def get_size(bb, sizex, sizey):
    """ Returns a size in pixels of X and Y dimensions of a picture
        such that the picture fits sizex, sizey size constraints and 
        keeps the aspect ratio
    """
    width = bb[2]-bb[0]
    height = bb[3]-bb[1]
    mult = 1

    if width > height:
        mult = sizex/width
        if height*mult > sizey:
            mult = sizey/height*mult
    else:
        mult = sizey/height
        if width*mult > sizex:
            mult = sizex/width*mult

    return (int(width*mult), int(height*mult))

def db_commit():
    try:
        db_session.commit()
        return jsonify(status='succ')
    except IntegrityError:
        db_session.rollback()
        return abort(409)

def stringify_class(results, one=False):
    ret = None
    if not one:
        ret = []
        for result in results:
            ret.append(stringify_one(result))

    else:
        ret = stringify_one(results)
    return ret

def stringify_one(result):
    ''' Stringifies an instance of the class,
        ignoring the masked methods and caching 
        post body rendering '''

    obj = {}
    for el in result.__dict__:
        if el == 'id' or \
                el == 'password' or \
                el == 'password_swapped' or \
                el == 'salt' or \
                isinstance(result.__dict__[el], state.InstanceState):
                    continue
        elif isinstance(result.__dict__[el], datetime):
            obj[el] = unicode(result.__dict__[el])
        elif el == 'body':
            rv = g.cache.get('astronet-post'+obj[string_id])
            if not rv:
                rv = markdown(resul.__dict__[el])
                g.cache.set('astronet-post'+obj[string_id],
                        rv, time=60*5)
            obj[el] = rv
        else:
            obj[el] = result.__dict__[el]
    return el

class FoundExc(Exception):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return self.value
