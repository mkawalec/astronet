class CommentBox
    constructor: (post_id, parent=null) ->
        box = document.createElement 'div'
        $(box).attr 'class', 'comment_box'

        body = document.createElement 'div'
        $(body).attr 'class', 'body'
        
        comment_input = document.createElement 'textarea'
        $(comment_input).attr 'class', 'input'

        body.appendChild comment_input

        send_btn = document.createElement 'button'
        $(send_btn).attr 'class', 'send_button btn btn-primary'
        $(send_btn).text 'Wyślij'

        $(send_btn).bind 'click', (event) =>
            $(send_btn).text 'Wysyłanie'

            $.ajax {
                type: 'POST'
                url: script_root + '/api/comments/' + post_id
                data:
                    parent: parent
                    post: post_id
                    body: $.trim comment_input.value
                success: (data) =>
                    $(box).hide 'fast'
                error: (data) =>
                    $(send_btn).text 'Błąd!'
            }

        box.appendChild body
        box.appendChild send_btn

        return box

class Comment
    constructor: (@tree, @i, @level, @post_id, @parent=null) ->
        @wrapper = $('.comments_wrapper')[0]
        @id = @tree[@i].comment['string_id']

        @bootstrap()
        return

    bootstrap: ->
        comment = @tree[@i].comment

        @comment = document.createElement 'div'
        $(@comment).attr 'class', "comment level#{@level}"
        $(@comment).attr 'data-string_id', comment['string_id']

        @body = document.createElement 'div'
        $(@body).attr 'class', 'body'
        $(@body).html comment['body']

        @timestamp = document.createElement 'div'
        $(@timestamp).attr 'class', 'timestamp'
        $(@timestamp).html comment['timestamp']

        if (parseInt uid) == comment['author']
            @delete = document.createElement 'div'
            $(@delete).text 'X'
            $(@delete).bind 'click', (event) =>
                $.ajax {
                    type: 'DELETE'
                    url: script_root+'/api/comment/'+comment['string_id']
                    success: (data) =>
                        if data.status == 'succ'
                            $(@comment).hide 'fast'
                            # TODO: Add getting the actual comment
                            # from the server
                    error: (data) =>
                        console.log 'error'
                }

            @comment.appendChild @delete
        
        @author = document.createElement 'div'
        $(@author).attr 'class', 'author'
        # TODO: Show some useful details about an author and not
        # her string id:D
        $(@author).html comment['author']

        @comment_box = new CommentBox @post_id, comment['string_id']

        @write_btn = document.createElement 'a'
        $(@write_btn).attr 'href', '#'
        $(@write_btn).text 'Odpowiedz'
        $(@write_btn).bind 'click', (event) =>
            event.preventDefault()
            $(@comment_box).toggle 'fast'

        @children_box = document.createElement 'div'
        $(@children_box).attr 'class', 'children_box'

        @comment.appendChild @author
        @comment.appendChild @timestamp
        @comment.appendChild @body

        if uid.length > 0
            @comment.appendChild @write_btn
            @comment.appendChild @comment_box

        @comment.appendChild @children_box

        $(@comment_box).hide()
        @append()

    append: ->
        if @parent == null
            @wrapper.appendChild @comment
        else
            parent = $(".comment[data-string_id='#{@parent}'] .children_box")[0]
            parent.appendChild @comment

        for child in @tree[@i].children
            @children.push (new Comment @tree, child, @level+1, @post_id, @id)

    children: []

class CommentList
    constructor: (@holder, @post_id) ->
        @bootstrap()
        return 0
    
    bootstrap: ->
        @comms_wrapper = document.createElement 'div'
        $(@comms_wrapper).attr 'class', 'comments_wrapper'

        @add_new = document.createElement 'div'
        $(@add_new).attr 'add_new_comment'

        @holder.appendChild @add_new
        @holder.appendChild @comms_wrapper

        if uid.length > 0
            @holder.appendChild (new CommentBox @post_id)
        else
            @notice = document.createElement 'div'
            $(@notice).attr 'class', 'notice'
            $(@notice).text 'Zaloguj się by dodawać komentarze'
            @holder.appendChild @notice

        $.ajax {
            type: 'GET'
            url: script_root + '/api/comments/' + @post_id
            success: (data) =>
                if data.status == 'db_null_error'
                    return 0

                @comments = data.comments
                # Generate comments starting from the top nodes
                @print_comments()
            error: (data) =>
                console.log 'errror, error'
                console.log data
        }

    print_comments: () ->
        for child in @comments[0].children
            @comments.push (new Comment @comments, child, 0, @post_id)


    clean: ->
        for child in @holder.children
            @holder.removeChild @holder.children[0]
        @bootstrap()
    
    comments: []
