var http = require('http');
var url = require('url');
var fs = require('fs');
var qs = require('querystring');

http.createServer(function (req, res) {
	res.writeHead(200, {'Content-Type': 'text/html'});
	fs.readFile('scouting.html', function(err, data) {
		res.write(data);
		res.end();
  	});

	if (req.method === 'POST') {
		var data = '';

		req.on('data', function(chunk) {
			data += chunk;
		});

		data += '\n'

		req.on('end', function() {

			fs.appendFile('data.txt', data, function(err) {

				if(err) throw err;

			})
	
		});
	}

}).listen(8080);