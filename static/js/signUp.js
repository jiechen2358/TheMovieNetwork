$(function(){
	$('#btnSignUp').click(function(){
		$.ajax({
			url: '/signUp',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.responseText);
                console.log(textStatus);
                console.log(errorThrown);
                alert(`btn js error`);
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