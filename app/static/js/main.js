$('.showrefresh').click(function() {
	$('.hidden-refreshing').removeClass('hidden');
});

var options = {
  valueNames: [ 'computername', 'inactiveusers', 'activeusers' ]
};

var userList = new List('users', options);