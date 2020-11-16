/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        var indice = $('#filter_by_indice').val();
        var sector = $('#filter_by_sector').val();
        var phase = $('#filter_by_phase').val();

        var i = data[1] || ""; // use data for the indice column
        var s = data[2] || ""; // use data for the sector column
        var p = data[4] || ""; // use data for the phase column

        if ( ( indice != "" && i != indice ) ||
            ( sector != "" && s != sector ) ||
            ( phase != "" && p != phase ) )
        {
            return false;
        }
        return true;
    }
);

// Call the dataTables jQuery plugin
$(document).ready(function() {
    var table = $('#dataTable').DataTable();
    // Event listener to the two range filtering inputs to redraw on input
    $('#filter_by_indice, #filter_by_sector, #filter_by_phase').change( function() {
        table.draw();
    } );
});
