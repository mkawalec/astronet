# Get the left/top offsets of an element
get_offsets = (element) ->
    offset = [element.offsetLeft, element.offsetTop]
    while element = element.offsetParent
        offset[0] += element.offsetLeft
        offset[1] += element.offsetTop
    return offset

# Show the user that the update was successful
status_notify = (object, what) ->
    bg_color = $(object).css 'background-color'
    border_color = "#CCCCCC"
    if ($(object).css 'border-color').length > 0
        border_color = $(object).css 'border-color'
    else if ($(object).attr 'style')?
            # A super-regex for matching any colour format (known to me)
            border_color = (((($(object).attr 'style').match /border-color:(#[0-9A-F]{6})|(rgb\((\d+),\s*(\d+),\s*(\d+)\))/)[0]).match /#([0-9A-F]{6})|(rgb\((\d+),\s*(\d+),\s*(\d+)\))/)[0]
    
    switch what
        when "success"
            ($(object).stop().animate {'background-color': '#99EE99', 'border-color': '#EAFF00'},
                500).animate {'background-color': bg_color,'border-color': border_color}, 500
        when "error"
            ($(object).stop().animate {'background-color': '#EE9999', 'border-color': '#EE0000'},
                500).animate {'background-color': bg_color,'border-color': border_color}, 500
            console.log 'error, error'

# Converts decimal to hex
decimal_to_hex = (decimal) ->
    hex = decimal.toString(16)
    if hex.length == 1
        hex = '0' + hex
    return hex

# Converts hex to decimal
hex_to_decimal = (hex) ->
    return parseInt hex, 16

# Generates an opposite colour
return_opposite = (colour) ->
    colour = rgb2hex colour
    return '#' + (decimal_to_hex (255-hex_to_decimal colour.substr 0,2)).toString() +
        (decimal_to_hex (255-hex_to_decimal colour.substr 2,2)).toString() +
        (decimal_to_hex (255-hex_to_decimal colour.substr 4,2)).toString()

rgb2hex = (rgb) ->
    rgb = rgb.match /^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/
    return (hex rgb[1]) + (hex rgb[2]) + (hex rgb[3])

hex = (x) ->
    return if isNaN(x) then "00" else hexDigits[(x - x % 16) / 16] + hexDigits[x % 16]

hexDigits = new Array("0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f")

# Choose a minimum of a two numbers
min = (first, second) ->
    if first < second
        return first
    return second

# Choose a max of a two numbers
max = (first, second) ->
    if first > second
        return first
    return second

# Destroy a loader
destroy_loader = ->
    document.body.removeChild $('#app_loader')[0]
    return 0

# Create a sonic loader
# TODO: Should the loader close when clicked?
create_loader = (timeout=1000)->
    loader = new Sonic {
        width: 100
        height: 100

        stepsPerFrame: 1
        trailLength: 1
        pointDistance: .025

        strokeColor: '#05E2FF'

        fps: 20

        setup: () ->
            this._.lineWidth = 2
        step: (point, index) ->

            cx = this.padding + 50
            cy = this.padding + 50
            _ = this._
            angle = (Math.PI/180) * (point.progress * 360)

            this._.globalAlpha = Math.max(.1, this.alpha)

            _.beginPath()
            _.moveTo(point.x, point.y)
            _.lineTo (Math.cos(angle) * 35) + cx, (Math.sin(angle) * 35) + cy
            
            _.closePath()
            _.stroke()

            _.beginPath()
            _.moveTo (Math.cos(-angle) * 32) + cx, (Math.sin(-angle) * 32) + cy
            _.lineTo (Math.cos(-angle) * 27) + cx, (Math.sin(-angle) * 27) + cy
       
            _.closePath()
            _.stroke()
        path: [
            ['arc', 50, 50, 40, 0, 360]
        ]
    }

    loader.play()

    background = document.createElement 'div'
    $(background).attr 'id', 'app_loader'
    $(background).attr 'style', 'width: 100%; height: 100%; opacity: 0.9;
                                 background-color: #000000; position: fixed;
                                 top:0; left: 0;vertical-align:middle'
    loader_elem = loader.canvas
    $(loader_elem).attr 'style', 'position:absolute;top:50%;margin-top:-50px;
                                  left:50%;margin-left:-50px;'
    background.appendChild loader.canvas
    document.body.appendChild background

    setTimeout('destroy_loader()', 1000*timeout)

rgb2hsv = (hex) ->
    red = hex_to_decimal hex.substr 1,2
    green = hex_to_decimal hex.substr 3,2
    blue = hex_to_decimal hex.substr 5,2
    hue = 0; sat = 0; f = 0; i = 0

    x = min (min red, green), blue
    val = max (max red, green), blue

    if x != val
        if red == x
            f = green-blue
            i = 3
        else
            if green == x
                f = blue-red
                i = 5
            else
                f = red-green
                i = 1
        hue = ((i-f/(val-x))*60)%360
        sat = (val-x)/val
    return [hue,sat,val]

# Returns a nicely formatted date
Date::format_nicely = ->
    year = this.getFullYear()
    month = parseInt(this.getMonth())+1
    day = this.getDate()
    hours = this.getHours()
    minutes = this.getMinutes()

    if month < 10
        month = '0' + month
    if day < 10
        day = '0' + day
    if hours < 10
        hours = '0' + hours
    if minutes < 10
        minutes = '0' + minutes
    
    return "#{year}/#{month}/#{day} #{hours}:#{minutes}"

# Print a nice file size
get_nice_size = (file_size) ->
    for app in ['B', 'KB', 'MB', 'GB', 'TB']
        if file_size < 1024
            return file_size + app
        file_size = Math.round file_size/1024

    return -1

# Calculate entropy for a given password
calculate_entropy = (pass) ->
    possible_symbols = 0
    
    numbers = /[0-9]/
    small_case = /[a-z]/
    large_case = /[A-Z]/
    others = /\!\@\#\$\%\^\*\(\)\,\.\<\>\~\`\[\]\{\}\\\/\+\=\-\s/
    if !pass.match numbers
    else
        possible_symbols += 10

    if !pass.match small_case
    else
        possible_symbols += 26

    if !pass.match large_case
    else
        possible_symbols += 26
    if !pass.match others
    else
        possible_symbols += 25

    if possible_symbols == 0
        return -1

    return Math.round(pass.length*
                      Math.log(possible_symbols)/Math.log(2))

# Return a nice string description of a number
nicefy_time = (number) ->
    endings = [ {ending: ' ns', amount: Math.pow(10, -9)},
                {ending: ' μs', amount: Math.pow(10, -6)},
                {ending: ' ms', amount: Math.pow(10, -3)},
                {ending: ' s', amount: 1},
                {ending: ' min', amount: 60},
                {ending: ' godzin', amount: 60*60},
                {ending: ' dni', amount: 60*60*24},
                {ending: ' lat', amount: 60*60*24*365},
                {ending: ' tysięcy lat', amount: 60*60*24*365*1000},
                {ending: ' milionów lat', amount: 60*60*24*365*1000*1000}]
    for i in [0..endings.length]
        if i == 0
            if number < endings[0].amount
                return Math.round(number/endings[0].amount) + endings[0].ending
        else if i == endings.length-1
            return Math.round(number/endings[i].amount) + endings[i].ending

        if endings[i].amount <= number < endings[i+1].amount
            return Math.round(number/endings[i].amount) + endings[i].ending


# Alert a user in somewhere
alert_user = (placeholder_id, message, alert_type) ->
    for child in $("##{placeholder_id} div.alert div.message_wrapper")
        if ($.trim $(child).html()) == ($.trim message)
            return 0

    alert = document.createElement 'div'
    $(alert).attr 'class', "alert alert-#{alert_type} fade in"

    close_button = document.createElement 'button'
    $(close_button).attr 'class', 'close'
    $(close_button).attr 'data-dismiss', 'alert'
    $(close_button).text 'x'
    $(close_button).bind 'click', (event) ->
        $(alert).hide 'slide', 'fast', ->
            $(alert).parent()[0].removeChild this

    message_wrapper = document.createElement 'div'
    $(message_wrapper).attr 'class', 'message_wrapper'
    $(message_wrapper).html message

    alert.appendChild close_button
    alert.appendChild message_wrapper
    $(alert).hide()

    $("##{placeholder_id}")[0].appendChild alert
    $(alert).show 'slide', 'fast'
    return 0

# True if an object is in array
exists_in = (object, array) ->
    for obj in array
        if obj == object
            return true
    return false


# Extends the array class with poping an element with a given id
Array::pop_id = (obj_id) ->
    for i in [this.length-1..0]
        if parseInt(this[i].id) == parseInt(obj_id)
            this.splice(i,1)
            return true
    return false

# Gets a bounding box for an image
getbbox = (width, height, t_width=180, t_height=170) ->
    width = parseInt(width)
    height = parseInt(height)

    mult = 1
    mult = t_width/width
    if mult*height > t_height
        mult = mult*t_height/height
    return [mult*width, mult*height]

# Checks a json return status. A decorator
chk_status = (waiter=null) -> (method) -> ->
    console.log arguments[0].status
    if waiter?
        clearInterval waiter

    if arguments[0].status == 'succ'
        return method.apply @, arguments
    else
        return method.apply ajax_error, [arguments[0], 'error']

ajax_error = (data) ->
    console.log 'error'
    console.log data

# Boolean tester
bool = (value) ->
    if value instanceof Boolean
        return value
    return !((/^(False)|(false)$/).test value)
