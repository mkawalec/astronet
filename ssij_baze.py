# -*- coding: utf-8 -*-
import os
import sys
import urllib2


#dla każdego pliku w DANE dokonano konwersji kodowania:
# for i in `ls`; do iconv -f ISO-8859-2 -t utf8 $i > "nowy"$i; done

def zassij():
    """Get astronews from ADRES to the number of RAN and save files in PATH """
    adres="http://news.astronet.pl/"
    path = "dane/"
    ran=7100
    for id in range(ran):
        u = urllib2.urlopen(adres+str(id))
        localFile = open(path+str(id), 'w')
        localFile.write(u.read())
        localFile.close()


def wywal_nie_ma_newsa():
    """ If there is information that a post with this numebr doesn't exist - delete file. """
    plik = open('dane/lista', 'rb')
    #print plik.read()
    for line in plik.readlines():
        a=line.split("<B>ID ")[1].split("</B>")[0]
        try:
            os.remove('dane/'+a)
        except:
            pass


def remove_lines():
    """Remove first 80 and last 50 lines to get rid of redundant and not important data."""
    path = 'danekod/'
    lista = os.listdir(path)
    i = 0
    l = len(lista)
    for f in lista:
        if i%100 == 0:
            print i*100.0/l
        i += 1
        id = str(f[4:])
        plik  = open(path+f, 'rb')
        plik2 = plik.readlines()[80:-50]
        localFile = open(path+id, 'w')
        for line in plik2:
            localFile.write(line)
        localFile.close()
        os.remove(path+f)







def get_title(nr):
    """Returns title of article (string) """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            return line.split("</SPAN><BR><SPAN CLASS=\"bigger\"><B>")[1].split("</B></SPAN></TD>")[0]
        except:
            pass

def get_lead(nr):
    """Returns lead of article (string) """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            return line.split('<BR><SPAN CLASS="midder">')[1].split('</SPAN><BR><BR>')[0]
        except:
            pass
        
def get_body(nr):
    """Returns main part of article (string) """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    start = False
    ans = ""
    for line in text:
        if '<SMALL>Dodał: ' in line:
            return ans
            break
        if start:
            ans += line
        if '<TR><TD><SPAN CLASS="midder">' in line:
            start = True

def get_author(nr):
    """Returns author(s) of article (string) """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    ans = ""
    #for line in text:
        #if "<I>Artykuł przygotow" in line:
            #return line.split("<I>Artykuł przygotow")[1].split(".</I>")[0]
    for line in text:
        try:
            if line.split('<SMALL><BR>Dodał')[1].split('>')[1].split('</A>')[0] != None:
                return ans+line.split('<SMALL><BR>Dodał')[1].split('>')[1].split('</A')[0]
                break
        except:
            pass
        try:
            if line.split('<SMALL>Dodał')[1].split('>')[1].split('</A')[0] != None:
                return ans+line.split('<SMALL>Dodał')[1].split('>')[1].split('</')[0]
                break
        except:
            pass

            
def get_update(nr):
    """Returns last update time (string) or None """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            if line.split('<SMALL><BR>Uaktualnił')[1].split('>')[2].split(' - ')[1][:19] != None:
                return line.split('<SMALL><BR>Uaktualnił')[1].split('>')[2].split(' - ')[1][:19]
                break
        except:
            pass
        try:
            if line.split('<SMALL>Uaktualnił')[1].split('>')[2].split(' - ')[1][:19] != None:
                return line.split('<SMALL>Uaktualnił')[1].split('>')[2].split(' - ')[1][:19]
                break
        except:
            pass

def get_date(nr):
    """Returns date of article (string) """
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            return line.split('<SMALL>Dodał')[1].split('>')[2].split(' - ')[1][:19]
            #if line.split('<SMALL><BR>Dodał')[1].split('>')[1].split('</A>')[1] != None:
                #print line
            #return line.split('<SMALL><BR>Dodał')[1].split('>')[1].split('<')[1]
        except:
            pass
            
def get_source(nr):
    """Returns source of article (string) or None if there is no source."""
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            if line.split('<SMALL><BR>Źródło:')[1].split('HREF="')[1].split('">')[0] != None:
                return line.split('<SMALL><BR>Źródło:')[1].split('HREF="')[1].split('">')[0]
        except:
            pass
        
def get_readers(nr):
    """Returns number of article readers or None."""
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines()
    for line in text:
        try:
            return line.split('<BR><BR>W całości newsa przeczytało osób: ')[1][:-1]
        except:
            pass    

def get_image(nr):
    """Returns tuple of image information (url, descri) or None if there is no image in an article."""
    path = 'danekod/'
    text = open(path+str(nr), 'rb').readlines() 
    lis = []
    ans = ""
    start = False
    nr = ""
    source = ""
    description = ""
    date = ""
    author = ""
    min = ""
    alt = ""
    for line in text:
        if '</TR></TABLE>' in line:
            start = False
            lis.append((nr, source,  description, date, author, min, alt,))
            ans = ""
        if start:
            ans += line
            if 'ALT="' in line: 
                alt = line.split('ALT="')[1].split('" BORDER')[0]
            if 'ALT="' in line: 
                min = line.split('ALT="')[0][5:-2].split('" BORDER')[0]
            if '<SMALL><BR>Dodał' in line:
                author = line.split('">')[1].split('</A')[0]
                date = line.split('">')[1].split('</A')[1][4:-12]
            if '<TD VALIGN=TOP>' in line:
                description = line[15:-5]
            if '<SMALL><BR>Źródło' in line:
                source = line.split('HREF="')[1].split('">')[0]
        if 'http://www.astronet.pl/redir.cgi?' in line:
            start = True
            nr = line.split('http://www.astronet.pl/redir.cgi?')[1].split('">')[0][2:]
    return lis[1:-1]


## Testing
#print get_image(7098)[2]
for i in range(1,7100,200):
    try:
        pass
        #print get_image(i)
        #print get_readers(i)
        #print get_body(i)
        #print i
        #print get_lead(i)
        #print get_date(i)
        #print get_author(i)
        #print get_data(i)
        #print get_source(i)
        #print get_update(i)
    except:
        pass

get_image(7098)

### Teraz:
## do tego: obrazek - link, opis, kto dodał



### Na później:
## obrazek - wybieranie dokładnego adresu do linku?
## author - gdy redakcja publikowala "<I>Artykuł przygotow"
## zbieranie linkow ze zrodel?
## zebranie komentarzy




