const path = require('path');
const express = require('express');
const app = express();
const port = 8000;
app.use('/public', express.static('public'))
app.get('/', function (req, res){
	res.sendFile(path.join(__dirname+'/index.html'));
});

app.listen(port);
console.log('Listening to port '+port)