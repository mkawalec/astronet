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
              

class FormAjaxify
    constructor: (form_id, redirect_to=null) ->
        @bind_form form_id, redirect_to

        return 0

    bind_form: (form_id, redirect_to) ->
        @form = $("##{form_id}")[0]
        @submit_btn = $("##{form_id} .btn-submit")

        @submit_btn.bind 'click', (event) =>
            event.preventDefault()
            # TODO: Make it work for a general form (too sleepy now
            # to make it sane)
            $.ajax {
                url: script_root + '/api/post'
                type: 'POST'
                data:
                    title: $('#input_title')[0].value
                    lead: $('#input_lead')[0].value
                    body: $('#input_body')[0].value
                success: chk_status() =>
                    status_notify @form, 'success'
                error: (data) =>
                    ajax_error data
            }

            return 0


render = new MarkdownRender()

# Zdecydowałem na razie, że nie będę Ajaxował tego forma
#form = new FormAjaxify('add_post')
