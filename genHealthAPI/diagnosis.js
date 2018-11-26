var request=require('request');
var app=require('./app');
var diseaseArray=new Array();
var diagnosis=(sex,age,id,choice_id,condition,callback)=>{
  
    var elem=new Array();
    elem[0]={
        id:id,
        choice_id:choice_id
    };
    var jsonObj={
        sex:sex,
        age:age,
        evidence:elem
    };
    request({
        url:'https://api.infermedica.com/v2/diagnosis',   //change all this
        headers: {
           'Content-Type': 'application/json',
           'app_id': 'b13bb615',
           'app_key':'09ad0cc482754a79c300840024f34726'
         },
         body:jsonObj,
         method:'POST',
         json:true  //why this?
          
       },(error,res,body)=>{
            delete elem;
            delete jsonObj;
           console.log('hereIN2');
           if(error)
           {
               callback('Unable to connect to server: ');
               //console.log('Unable to connect to server: '+error);
           }
           else{
               if(body.question!=null){
               var Ques=body.question.text;
               var options_arr=body.question.items; //object's array
               var options=[];
               var conditions_arr=body.conditions;
               var conditions=[];
               for(var i=0;i<conditions_arr.length;i++)
               {
                   var obj={
                       name:conditions_arr[i].common_name,
                       prob:conditions_arr[i].probability
                   };
                   conditions[i]=obj;
               }
               var opt="";
               for(var i=0;i<options_arr.length;i++)
               {
                   var obj={
                       id:options_arr[i].id,
                       name:options_arr[i].name
                   };
                   options[i]=obj;
                   console.log(options[i].id);
                   opt=opt+i+1;
                   op=opt+". ";
                   opt=opt+options[i].name;
                   opt=opt+" ";
               }
               Ques=Ques+" "+opt;
               console.log(Ques);
               
            app.askQuestion(Ques,function(x){
                if(x<=0)
           diagnosis(sex,age,options[0].id,'absent',conditions);
          else
            diagnosis(sex,age,options[x-1].id,'present',conditions);
        if(typeof callback=="function")
             callback();
            });
            
            }
            else{
                diseaseArray.concat(condition);
            }
             
       }
           
       });
}
//call app.js to print the main array!
module.exports.diagnosis=diagnosis;