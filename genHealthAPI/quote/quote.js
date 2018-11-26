var request=require('request');

var quote=(callback)=>{

    request({
        url:'http://quotes.rest/qod.json',
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
                quote:body.contents.quotes[0].quote,
                author:body.contents.quotes[0].author
            });
        }}
    });
}
module.exports.quote=quote;