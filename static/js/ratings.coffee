$ ->
    $('div.voting a.vote').click (event) ->
        event.preventDefault()
        direction = $(event.target).attr('rel')
        data_obj = $(event.target).siblings('span.score')
        content_type = data_obj.attr('data-content-type')
        obj_pk = data_obj.attr('data-obj-pk')
        on_success = (data, textStatus, jqXHR) ->
            data_obj.text(data)
        $.get('/ratings/vote/', {content_type: content_type, obj_pk: obj_pk, direction: direction}, on_success, 'text')