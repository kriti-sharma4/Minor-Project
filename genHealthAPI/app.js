var request=require('request');
const diagnose=require('./diagnosis');
const parser=require('./parse');
const path = require('path');
const http=require('http');
const express = require('express');
const socketIO = require('socket.io');
const publicPath = path.join(__dirname);
const port = 3000;
var app = express();
var server = http.createServer(app);
var io = socketIO(server);
var index=-10;
app.use(express.static(publicPath));
io.on('connection', (socket) => {
    console.log('New user connected');
    var name="";
    var age=0;
    var sex="";
    var x=0;
    var ans=[];
    var ques=['Hi!Your name please','Your age Please','Your Sex?'];

    socket.emit('botText',{
        text:ques[x]
    });  

socket.on('botReply',(message)=>{

if(x<3){
    ans[x]=message.text;
    console.log(ans[x]);
    x++;
    newQuestion();
}
if(x==3)
{
    x++;
   socket.emit('botText',{
       text:'Enter your Query.'
   });

   socket.on('botReply',(message)=>{
       parser.parse(ans[2],ans[1],message.text);
       
    });

}
 });

 
 function newQuestion(){
    if(x<3){
    socket.emit('botText',{
        text:ques[x]
    });
   }
}
function askQuestion(Ques,callback)
{
    socket.emit('botText',{
        text:Ques
    });
    var x;
    socket.on('botReply',(message)=>{
       if(typeof callback=='function')
         callback(message.text);
        });
}
module.exports.askQuestion=askQuestion;
   });

server.listen(port, () => {
    console.log(`Server is up on ${port}`);
  });
//module.exports.askQuestion=askQuestion;