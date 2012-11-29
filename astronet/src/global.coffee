### 
# Script ran on every page
###

mark_current_page = ->
    console.log window.location.href
    for child in $('ul.nav')[0].children
        console.log $(child.children[0]).attr 'href'
        if (window.location.href.indexOf $(child.children[0]).attr 'href') != -1
            $(child).attr 'class', 'active'
            break

    return 0

mark_current_page()
