var active_html = '<i class="small material-icons light-blue-text">visibility</i>';
var inactive_html = '<i class="small material-icons blue-grey-text text-lighten-5">visibility_off</i>';
var verified_html = '<i class="small material-icons light-blue-text">verified_user</i>';
var unverified_html = '<i class="small material-icons blue-grey-text text-lighten-5">verified_user</i>';

function toggle_active_state() {
    $container = $( this )
    user_id = $container.attr("dc-user-id");
    DigiCubes.toggleUserActiveState(user_id)
    .then( (data) => {
        if (data.state === true) {
            $( this ).html(active_html);
        } else {
            $( this ).html(inactive_html);
        }        
    });
};

function toggle_verified_state() {
    $container = $( this )
    user_id = $container.attr("dc-user-id");
    DigiCubes.toggleUserVerifiedState(user_id)
    .then( (data) => {
        if (data.state === true) {
            $( this ).html(verified_html);
        } else {
            $( this ).html(unverified_html);
        }
    });
};

function init() {
    $("td[dc-state=active").each(function( index ) {
        $( this ).html(active_html);
        $( this ).addClass("dc-clickable");
        $( this ).click(toggle_active_state);
    });

    $("td[dc-state=inactive").each(function( index ) {
        $( this ).html(inactive_html);
        $( this ).addClass("dc-clickable");
        $( this ).click(toggle_active_state);
    });

    $("td[dc-state=verified").each(function( index ) {
        $( this ).html(verified_html);
        $( this ).addClass("dc-clickable");
        $( this ).click(toggle_verified_state);
    });

    $("td[dc-state=unverified").each(function( index ) {
        $( this ).html(unverified_html);
        $( this ).addClass("dc-clickable");
        $( this ).click(toggle_verified_state);
    });
};
