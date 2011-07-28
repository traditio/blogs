$ ->
    $('a.reply').click (event) ->
        event.preventDefault()
        event_parent = $(event.target).parent('li')
        child_ul = event_parent.children('ul')
        parent_pk = event_parent.attr('data-parent-pk')
        if (event_parent.children('form').length > 0) is false
            form = $($('#template-comments-form').html())
            form.find('input[name=parent]').val(parent_pk)
            if child_ul.length > 0
                form.insertBefore(child_ul)
            else
                form.appendTo(event_parent)
            form.slideToggle()
        else
            event_parent.find('> form').slideToggle()