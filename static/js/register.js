$(function(){
	$('#btnRegister').click(function(){
		
		$.ajax({
			url: '/register',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});