// TOOLTIPS
/**
 * Function to initialize all tooltips on a page
 **/
$(function() {
  $('[data-toggle="tooltip"]').tooltip()
});


// RESET TICKETS FILTERS
/** 
 * Onclick functions for the ticket type and status filters.
 * Function that clears the filters after reset button is clicked by a user
 **/
$('#reset').click(function() {
  $("#ticket-type").val($("#ticket-type option:first").val());
  $("#ticket-status").val($("#ticket-status option:first").val());
});


$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  e.target // newly activated tab
  e.relatedTarget // previous active tab
});

// DISPLAY EDIT COMMENT FORM

/** 
 * Function that displays only the comment form which user chose to update.
 * Function is initiated on edit button click.
 * When users clicks 'edit' button card view is hidden and editable comment is
 * being displayed
 **/

$(document).ready(function() {
  // Hide all (update) form as a default
  $('.edit-comment').hide();
  $('.edit-comment-btn').click(function() {
    $(this).parents('div.card-header').nextAll('.posted-comment').hide();
    $(this).parents('div.card-header').nextAll('.edit-comment').show();
  });
});

// CHECK TRUNCATE

/**
 * Function that checks which comments were truncated in order to display
 * 'read more' link only for those comments
 **/

$(function() {
     $('.comment-text').each(function(index, elem) {

         if(elem.offsetWidth === elem.scrollWidth){
          	$(this).siblings('.read-more').hide();
         }
     });
 });
 
 // SHOW MORE / LESS COMMENT

/**
 * Function that toggles materialize class truncate for the comment text
 * in order to manage very long comments.
 * When comments are truncated link 'more' can be clicked to see full text.
 * On other other hand when user wants to hide the comment again he / she can 
 * click 'show less' which will truncate the comment 
 **/

// Show more
$(document).ready(function() {
  $(function() {
    $('.read-less').hide();
    $('.read-more').click(function() {
      $(this).siblings('.comment-text').toggleClass('text-truncate');
      $(this).hide();
      $(this).siblings('.read-less').show();
    });
  });
});

// Show less
$(document).ready(function() {
  $(function() {
    $('.read-less').click(function() {
      $(this).siblings('.comment-text').toggleClass('text-truncate');
      $(this).hide();
      $(this).siblings('.read-more').show();
    });
  });
});