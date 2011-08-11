$.Model "Num", {
    findAll: "/js/ajax/"
}, {
    identity: () ->
        "num_" + this.num
}

$.Controller 'Nums', {
    defaults :
        start: 1
        limit: 10
        nums: new Num()
}, {
    init: () ->
        this.callback('append')()
        this.delegate document.documentElement,'#more-nums', 'click', this.callback('append')

    append: () ->
        controller = this
        $.when(Num.findAll {start: controller.options.start, limit: controller.options.limit}).done (nums) ->
            if controller.nums?
                for n in nums
                    controller.nums.push(new Num(n))
            else
                controller.nums = nums
            controller.options.start += controller.options.limit
            controller.callback('display')(controller.nums)

    display: (nums) ->
        $(this.element).html '//js_templates/nums.ejs', {nums: nums}
}

$ () ->
    $('#nums').nums()