### 
# Script ran on every page
###

mark_current_page = ->
    closeness = new Array()

    for child in $('ul.nav')[0].children
        if (window.location.href.indexOf $(child.children[0]).attr 'href') != -1
            closeness.push {node: child,\
                            length: ($(child.children[0]).attr 'href').length}
    console.log closeness

    # Find the maximum value in the children
    [max, max_child] = [-1, null]
    for child in closeness
        if child.length > max
            max = child.length
            max_child = child.node

    if max_child?
        $(max_child).attr 'class', 'active'
    return 0

mark_current_page()
