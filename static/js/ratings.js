(function() {
  $(function() {
    return $('div.voting a.vote').click(function(event) {
      var content_type, data_obj, direction, obj_pk, on_success;
      event.preventDefault();
      direction = $(event.target).attr('rel');
      data_obj = $(event.target).siblings('span.score');
      content_type = data_obj.attr('data-content-type');
      obj_pk = data_obj.attr('data-obj-pk');
      on_success = function(data, textStatus, jqXHR) {
        return data_obj.text(data);
      };
      return $.get('/ratings/vote/', {
        content_type: content_type,
        obj_pk: obj_pk,
        direction: direction
      }, on_success, 'text');
    });
  });
}).call(this);
