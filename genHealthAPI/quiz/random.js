var request=require('request');

var random=(callback)=>{

    request({
        url:'http://jservice.io/api/random',
        json:true,
        method:'GET'
    },(error,response,body)=>{
        if(error)
          console.log(error);
        else{
            //console.log(body[0].question);
            //console.log(body[0].answer);
        if(callback){
            callback(undefined,{
                question:body[0].question,
                answer:body[0].answer
            });
        }}
    });
}
module.exports.random=random;