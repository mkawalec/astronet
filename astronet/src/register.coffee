# Notifies the user about her password strength
show_pass_strength = ->
    password = $("[name='passwd1']")[0]
    pass_strength = $('#pass_strength')

    entropy = calculate_entropy password.value.trim()
    $(pass_strength).text "Złamanie twojego hasła zajęłoby max
                           #{nicefy_time(Math.pow(2, entropy-32))}
                           na komputerze klasy PC"
 
$("[name='passwd1']").bind 'keyup', ->
    show_pass_strength()
