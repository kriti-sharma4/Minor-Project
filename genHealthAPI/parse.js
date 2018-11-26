var request=require('request')
var diagnose=require('./diagnosis');
var parse=(sex,age,Text,callback)=>{
  
    var jsonObj={    
      text:Text
          
    };
    request({
     url:'https://api.infermedica.com/v2/parse',
     headers: {
        'Content-Type': 'application/json',
        'app_id': 'b13bb615',
        'app_key':'09ad0cc482754a79c300840024f34726'
      },
      body:jsonObj,
      method:'POST',
      json:true  //why this?
       
    },(error,res,body)=>{
        console.log('hereIN');
        if(error)
        {
            //callback('Unable to connect to server: ');
            console.log('Unable to connect to server: '+error);
        }
        else{
            var n=body.mentions.length;
        //var arr=new Array();
        var arr2=body.mentions;
        for(var i=0;i<n;i++)
        {
        
            console.log(arr2[i].id);
            //var obj={
             //id:arr2[i].id,
            // choice_id:arr2[i].choice_id
            //};
            id=arr2[i].id;
            diagnose.diagnosis(sex,age,id,'present',null,function(){
                console.log('HI1');
                if(typeof callback=="function")
                  callback();
            });
            
        }
    }
        
    });
}

module.exports.parse=parse;