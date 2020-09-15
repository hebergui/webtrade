$(document).ready(function() {
    $('#edit-type-timeline select').change(function() {
        $('#button_timeline').show();
        $('#block_timeline').hide();
        $('#metadata_timeline').hide();
        $('#match_timeline').hide();

        if ($(this).val() == "block") {
            $('#block_timeline').show();
        }
        if ($(this).val() == "metadata") {
            $('#metadata_timeline').show();
        }
        if ($(this).val() == "match") {
            $('#match_timeline').show();
        }
    });
    $("#submit_timeline").click(function( event ) {
        if ($('#block_timeline').attr('style') == "") {
            url = '/timeline/' + $('#edit-type-timeline select').val() + '/' + $('#block_timeline select').val()
            event.preventDefault();
            location.href = url
        }
        if ($('#metadata_timeline').attr('style') == "") {
            url = '/timeline/' + $('#edit-type-timeline select').val() + '/' + $('#metadata_timeline select').val()
            event.preventDefault();
            location.href = url
        }
        if ($('#match_timeline').attr('style') == "") {
            url = '/timeline/' + $('#edit-type-timeline select').val() + '/' + $('#match_timeline select').val()
            event.preventDefault();
            location.href = url
        }
    });
});