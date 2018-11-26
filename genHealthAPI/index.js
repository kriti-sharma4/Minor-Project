//define(['require','app'],function(require){
require(['require','app'],function(require){
var app=require('./app');
var socket = io();
socket.on('connect', function () {
  console.log('Connected to server');
});

socket.on('disconnect', function () {
  console.log('Disconnected from server');
});

socket.on('botText',(message)=>{
   console.log(message.text);
});

var btn=document.getElementById('btn1');
btn.onclick=()=>{
    console.log("clicked");
socket.emit('botReply',{
  text:document.getElementById('insert').value
});
console.log('emitted');
}
});
