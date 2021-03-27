$(function(){
    $('#btnSignUp').click(function(e){
        e.preventDefault();
        $.ajax({
            url: '/signUp',
            data: $('form').serialize(),
            type: 'POST',
            async: false, // this is needed in order to get a proper response from server (server is doing a database query and thus takes long)
            success: function(response){
                alert(response)
                window.location.href = "/showSignIn"; // this is to redirect to signin page after a successful signup
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus);
                console.log(errorThrown);
                alert(jqXHR.responseText);
            }
        });
    });
});

function check_pass() { /* check if submit button should be enabled, default is disabled*/
    if(document.getElementById('inputUsername').value && document.getElementById('password').value && document.getElementById('confirm-password').value){
        if (document.getElementById('password').value == document.getElementById('confirm-password').value) {
            document.getElementById('btnSignUp').disabled = false;
        } else {
            document.getElementById('btnSignUp').disabled = true;
        }
    }
}