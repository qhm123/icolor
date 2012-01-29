function randomChar(l){
	var x = "0123456789abcdef";
	var tmp = "";
	for(var i = 0; i < l; i++){
		tmp += x.charAt(Math.ceil(Math.random() * 100000000) % x.length);
	}
	
	return tmp;
}
