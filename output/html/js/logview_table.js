 // Tool Tips
 $(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

/* Formatting function for row details  */
function rowformat ( d ) {
    // `d` is the original data object for the row
    return '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'+
        '<tr>'+
            '<td><Strong>RESULT:</strong></td>'+
            '<td><pre>'+d.result+'</pre></td>'+
        '</tr>'+
    '</table>';
}

// Datatables.net table
$(document).ready(function() {

    var table = $('#logview_table').DataTable( {
        "order": [[ 1, "desc" ]], // sort on raw timestamp
        "pageLength": 100,

    ajax: {
        url: 'data/beaconlogs.json',
        dataSrc: 'data'
    },
    columns: [
        {
            "className":      'details-control',
            //"orderable":      false,
            "data":           null,
            "defaultContent": ''
        },
                               // Column 0, button
        { data: 'timestamp' }, // Column 1, Human timestamp
        { data: 'timestamp' }, // Column 2, timestamp
        { data: "type" },      // Column 3, Beacon type
        { data: "beacon_id" }, // Column 4, Beacon ID
        { data: "user" },      // Column 5, User
        { data: "command" },   // Column 6, Command
        { data: 'result' }     // Column 7, result
    ],
    columnDefs: [
        {   // Left justify headers
            targets: [ 0, 1, 2, 3, 4, 5, 6, 7 ],
            className: 'dt-body-left'
        },
        { // Pre tags on commands
            targets: [ 6 ],
            render:function(data){
                return ("<pre>" + data + "</pre>");
            }

        },
        { // truncated Pre tags on results
            targets: [7 ],
            render: function ( data, type, row ) {
                return data.length > 50 ?
                "<pre>" + data.substr( 0, 50 ) +'</pre>' + '<p style="color:green";">truncated...</p>' :
                    "<pre>" + data + "</pre>";
            }

        },
        {   // Human Time
            targets: 2,
            render: function(data){
                //return moment(data);

                return moment(parseInt(data)).format("YYYY-MM-DD hh:mm:ss");
                
            }
        }

    ]

    } );

    // Add event listener for opening and closing row details
    $('#logviewTable').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( rowformat(row.data()) ).show();
            tr.addClass('shown');
        }
    } );

    
} );
