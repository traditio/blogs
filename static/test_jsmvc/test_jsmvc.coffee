$.Controller 'Nums', {
    init: () ->
        this.delegate document.documentElement,'#more-nums', 'click', more_nums
    more_nums: () ->
        alert(2)
}

$ () ->
    $('#nums').nums()