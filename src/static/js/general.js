(function() {

    var msisdnValidation = function(response){
        $("#error_msg").hide();
        if(response.message){
            $("#error_msg").show();
        }
    };

    var validateLoginForm = function(data, successFunc){
        $.ajax({
            url: window.registration_validation_url,
            data: data,
            dataType: 'json',
            success: function(data) {
                 successFunc(data);
            },
        })
    };

//    $("#id_password").on('focus', function(){
//        $("#msg").hide();
//    });
//
//    $("#id_password").on('blur', function(e){
//        var value = e.target.value;
//        validateLoginForm({
//            "password": value
//        }, passwordValidation);
//    });

    $("#id_mobile_no").on('focus', function(){
        $("#error_msg").hide();
    });

    /**
     * Restrict value to 12 digit
     * @param e keyup event
     */
    var validateInternationalPhoneNumber = function(e) {
        var value = e.target.value;
        if(value.length > 10) {
            e.target.value = value.substring(0, 10);
            return false;
        }
    };

    /**
     * Restrict non numeric values
     * @param e keypress event
     */
    var validateUsername = function(e) {
        var a = [];
        var k = e.which;

        for (var i = 48; i < 58; i++)
            a.push(i);

        if (!(a.indexOf(k)>=0))
            e.preventDefault();
    };

    $('#id_mobile_no').on('keypress', validateUsername);
    $('#id_mobile_no').on('keyup', validateInternationalPhoneNumber);

//    $("#id_mobile_no").on('blur', function(e){
//        var value = e.target.value;
//        validateLoginForm({
//            "username": value
//        }, msisdnValidation);
//    });
$("#app_id").click(function(event){
    var form_data=$("#app_form").serializeArray();
    for (var input in form_data){
		if (form_data[input]['name'] == 'mobile_no' && form_data[input]['value'].length!=10 && form_data[input]['value']!= ""){
		    $("#error_msg").show();
		    event.preventDefault();
		}
//		var valid=element.hasClass("valid");
//		var error_element=$("span", element.parent());
//		if (!valid){error_element.removeClass("error").addClass("error_show"); error_free=false;}
//		else{error_element.removeClass("error_show").addClass("error");}
	}
});
})();



