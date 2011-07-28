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
        console.group('parent_pk', parent_pk);
        console.group('form not exists, created new', form);
        if (child_ul.length > 0) {
          console.group('insert before child li', child_ul);
          form.insertBefore(child_ul);
        } else {
          console.group('append to', event_parent);
          form.appendTo(event_parent);
        }
        return form.slideToggle();
      } else {
        console.group('form exists', event_parent.children('form'));
        return event_parent.find('> form').slideToggle();
      }
    });
  });
}).call(this);
