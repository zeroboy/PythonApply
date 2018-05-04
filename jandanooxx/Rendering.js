var page = require("webpage").create();
var system=require('system');
var args = system.args;
var renderurl = "https://jandan.net/ooxx/page-"+args[1]+"#comments";

//console.log(renderurl);
page.onResourceRequested = function(request) {
  console.log('Request ' + JSON.stringify(request, undefined, 4));
};
page.onResourceReceived = function(response) {
  console.log('Receive ' + JSON.stringify(response, undefined, 4));
};

page.open(renderurl ,function(status){

    //console.log("status:"+status);
    //console.log();
	var body = page.evaluate(function(){
		return document.body.innerHTML;
	});
	console.log(body);
    phantom.exit();
});


//E:/wamp/www/application/pycharm/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe  E:/wamp/www/application/pycharm/project1/Rendering.js 354

/*
*  E:/wamp/www/application/pycharm/phantomjs-2.1.1-windows/phantomjs-2.1.1-windows/bin/phantomjs.exe --load-images=true  --config=E:/wamp/www/application/pycharm/project1/config.json  E:/wamp/www/application/pycharm/project1/Rendering.js 354
* */