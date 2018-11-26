var cron=require('node-cron');
var quote=require('./quote');
cron.schedule('12 50 12 * * *',()=>{
    console.log("here");
   quote.quote((error,result)=>{
     if(error)
      console.log(error);
    else{
        console.log(result.quote);
   console.log(result.author); 
    }
   });
 
});