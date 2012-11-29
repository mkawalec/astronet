class MarkdownRender
    constructor: ->
        @body = $('#input_body')[0]
        @render = $('#markdown_render')[0]
        @pane_switch = $("a[href='#rendered_tab']")[0]

        @activate()

    activate: ->
        $(@pane_switch).bind 'click', (event) =>
            @update_preview()

    update_preview: ->
        console.log 'updating'
        $.ajax {
            url: script_root + '/api/post/preview'
            type: 'POST'
            data:
                post_body: @body.value
            success: chk_status() =>
                data = arguments[0]
                console.log data

                $(@render).html data['preview']
            error: (data) =>
                ajax_error data
        }
                

render = new MarkdownRender()
