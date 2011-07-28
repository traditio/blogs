(function() {
  $(function() {
    return $('a.reply').click(function(event) {
      var child_ul, event_parent, form, parent_pk;
      event.preventDefault();
      event_parent = $(event.target).parent('li');
      child_ul = event_parent.children('ul');
      parent_pk = event_parent.attr('data-parent-pk');
      if ((event_parent.children('form').length > 0) === false) {
        form = $($('#template-comments-form').html());
        form.find('input[name=parent]').val(parent_pk);
        if (child_ul.length > 0) {
          form.insertBefore(child_ul);
        } else {
          form.appendTo(event_parent);
        }
        return form.slideToggle();
      } else {
        return event_parent.find('> form').slideToggle();
      }
    });
  });
}).call(this);
