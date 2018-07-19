$( document ).ready(function() {
    $( document ).tooltip({
        items: '.hoverShowImage',
        content: function(){
            return "<img src='/notebooks/" + $(this).attr('id') + "' />"
        }
    });
});
