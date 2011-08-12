$.Model "Friend", {
    destroyAll: (ids, success) ->
        success()
    destroy: (id, success) ->
        this.destroyAll([id], success)
}, {}


$.Controller 'RefferalsForm', {}, {

    "{list} remove": () ->
        this.callback('display')()

    "{list} remove" : (list, ev, items) ->
        items.elements(this.element).slideUp () ->
            $(this).remove()

    ".delete click": (el, ev) ->
        el.parent().model().destroy()
        
    "#add-one-more click": () ->
        this.options.list.push new Friend({id: this.options.list.length+1, name: '', email: ''})
        
    init: () ->
        for i in [0..2]
            this.options.list.push new Friend({id: i, name: '', email: ''})
        this.callback('display')()

    display: () ->
        this.element.html this.view('init', {friends: this.options.list})
}

$ () ->
    $('.refferals_form').refferals_form({list: new Friend.List([])})