
var net = require('net');

var clientHandler = function(socket){
    //客戶端傳送資料的時候觸發data事件
  socket.on('data', function dataHandler(data) {//data是客戶端傳送給伺服器的資料
    console.log(socket.remoteAddress, socket.remotePort, 'send', data.toString());
        //客戶向server傳送訊息
    socket.write('server received\n');
  });

    //當對方的連線斷開以後的事件
  socket.on('close', function(){
    console.log(socket.remoteAddress, socket.remotePort, 'disconnected');
  })
};

var app = net.createServer(clientHandler);
app.listen(8000, '140.116.72.75');
console.log('tcp server running on tcp://', '140.116.72.75', ':',8000);

