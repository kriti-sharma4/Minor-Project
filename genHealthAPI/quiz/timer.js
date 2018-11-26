var cron=require('node-cron');
var random=require('./random');
cron.schedule('59 17 12 * * *',()=>{
    console.log("here");
   random.random((error,result)=>{
     if(error)
      console.log(error);
    else{
        console.log(result.question);
   console.log(result.answer); 
    }
   });
 
});