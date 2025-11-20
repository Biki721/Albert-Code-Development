console.log('Health Check PRP')

// ************ PUBLIC FUNCTION *******************
function getCurrentTime(){
    var date = new Date();
    var localTime = date.getTime();
    var localOffset=date.getTimezoneOffset()*60000; 
    var utc = localTime + localOffset;
    offset =8;
    var SGT = utc + (3600000*offset);
    var time = new Date(SGT).toLocaleString();
    return time;
}

// add note to localStorage
function addLocalNote(msg){
    localStorage.note += msg;
    localStorage.note += getCurrentTime();
}

// *******************************************


if(localStorage.system == 'PRP' || location.href == 'http://16.202.11.196:8014/Services/SendMail.php'){
    console.log('PRP RUN')

    var testTime = 30000;

    if(location.href == 'https://partner.hpe.com/web/public/login'){
        checkSite();
    }

    if(location.href == 'http://16.202.11.196:8014/Services/SendMail.php'){
        var sendMailPHP = true;
    }else{
        var sendMailPHP = false;
        if(document.getElementsByTagName('title')[0].innerHTML.indexOf('Gateway Timeout') != -1){

            localStorage.site = 1;
            addLocalNote('/Gateway Timeout:')
            window.open("about:blank","_self").close();

        }else if(document.getElementsByTagName('title')[0].innerHTML.indexOf('Unavailable') != -1){
    
            localStorage.site = 1;
            addLocalNote('/Service unavailable:')
            window.open("about:blank","_self").close();

        }else if(document.getElementsByTagName('title')[0].innerHTML.indexOf('JBoss Web/7.0.17..Final-redhat-1 - Error report') != -1){
            
            localStorage.siteDXP = 1;
            addLocalNote('/JBoss Web/7.0.17..Final-redhat-1 - Error report:')
            window.open("about:blank","_self").close();

        }else if(document.getElementsByTagName('title')[0].innerHTML.indexOf('500 Internal Server Error') != -1){
            
            localStorage.siteDXP = 1;
            addLocalNote('/500 Internal Server Error:')
            window.open("about:blank","_self").close();

        }
    }

    var APJPlat = 'demoapjplat@pproap.com';
    var APJDis='demo_apj_distributor@pproap.com';
    var NAPlat='demo_na_platinum@pproap.com';
    // var APJSw='demoapjsw@pproap.com';
    var password = 'ExperiencePRP!';
    // ******************   LOGIN PAGE    ***************** 
    if(location.pathname == '/web/public/login' || location.pathname == '/login'){
        // wrong password will have this TYPE
        if(location.href.indexOf('TYPE') == -1){

            var handler = function(event){
                console.log('event.data')
                console.log(event.data);
                if(event.data != 'MessagePosted'){
                    // event.data为传过来的时间
                    var t = new Date().getTime();
                    console.log(t-event.data)
                    if(t-event.data > 60000){
                        localStorage.site = 1;
                        addLocalNote('/Login over 60s:')
                        
                        window.open("about:blank","_self").close();
                    }
                }
            }
            window.addEventListener("message",handler,false);

            var index = 0;
            // interval for login page loaded, if the form is not loaded
            var loginInterval = window.setInterval(function(){
                // if(jQuery('#content').length && jQuery('#_58_loginFm').length){
                if(jQuery('#content').length){
                    // form loaded
                    console.log('run login')
                    window.clearInterval(loginInterval);
                    // login
                    switch(parseInt(localStorage.failNo)){
                        case 0:
                        console.log('APJPlat login')
                        login(APJPlat,password);
                        break;
            
                        case 1:
                        console.log('APJDis login')
                        login(APJDis,password);
                        break;
            
                        case 2:
                        console.log('NAPlat login')
                        login(NAPlat,password);
                        break;
            
                        case 3:
                        triggerEmail('error');
                        break;
            
                        case 100:
                        triggerEmail('recover');
                        break;

                        case 101:
                        localStorage.failNo = 100;
                        location.href = "https://partner.hpe.com/web/public/login";
                        break;
                    }
                }
                // else{
                //     // form not loaded
                //     console.log(parseInt(localStorage.failNo))
                //     if(parseInt(localStorage.failNo) == 3){
                //         // already 3 times, identify as fail. Downtime case2!
                //         window.clearInterval(loginInterval);
                //         localStorage.failType = 2;
                //         triggerEmail('error');
                //     }else{
                //         // not 3 times yet, still try
                //         index++;
                //         if(index == 30){
                //             // If the form couldn't load in 30 seconds, note it as fail and formNo ++
                //             console.log('could not find login form');
                //             localStorage.failNo++;
                //             getTime();
                //             history.go(0); // refesh page
                //         }
                //     }
                // }
            },1000)

            function login(username,pwd){
                jQuery('#USER').val(username);
                jQuery('#PASSWORD').val(pwd);
                if(jQuery('#sign-in-btn').length == 0){
                    location.href = "https://partner.hpe.com/group/upp-apj";
                }else{  
                    jQuery('#sign-in-btn').click(); 
                }
            }

        }else{
            // login error message, page refresh, note this as fail. Downtime case3!
            window.setTimeout(function(){
                if(localStorage.failNo == 2){
                    localStorage.failType = 3;
                }
                localStorage.failNo++;
                getTime();
                location.href = "https://partner.hpe.com/login";
            },30000)
        }
    }


    // ******************   HOMEPAGE    ***************** 
    if(location.href == 'https://partner.hpe.com/group/upp-apj'){
        var index = 0;
        var hpCounting = 0;
        var checkInterval = window.setInterval(function(){
            console.log('hpCounting: ' + hpCounting)
            hpCounting ++; 
            if(hpCounting >15){
                addLocalNote("!!!!!!!!!!!!!!!!!PRP HOME PAGE NO RESPONSE!!!!!!!!!!!!!!!!!")
                localStorage.site = 1;
                
                window.open("about:blank","_self").close();
            }

            //console.log(localStorage.failNo)
            if(jQuery('#content').length){
                console.log('login success')
                // login successful
                if(localStorage.initial=='true'){
                    // Initial tool, no event.data transfer from previous login page
                    localStorage.initial = false;
                    localStorage.failNo = 100;
                    window.clearInterval(checkInterval);
                    localStorage.site = 0;
                    window.setTimeout(function(){
                        logout();
                    },3000)
                }

                // send message to previous login, to prove that the server is not down, and close previous window
                var handler = function(event){
                    console.log('event.data')
                    console.log(event.data);
                    // if(typeof(event.data) == 'string'){
                    //     mergeLogFile(event.data);
                    // }
                    var t = new Date().getTime();
                    console.log(t-event.data)
                    if(event.data){
                        if(t-event.data > 90000){
                            localStorage.site = 1;
                            addLocalNote('/Homepage over 90s:')
                            
                            window.open("about:blank","_self").close();
                        }else{
                            event.source.postMessage('MessagePosted',event.origin);
    
                            localStorage.failNo = 100; // set failNo 100 means success 
                            window.clearInterval(checkInterval);
                            if(event.origin == 'http://16.202.11.196:8014'){
                                // site必须设置成0，logout之后才会重置
                                localStorage.site = 0;
                            }
                            localStorage.overSite = 0;
                            window.setTimeout(function(){
                                logout();
                            },3000)
                        }
                    }else{
                        // Message haven't been posted to the homepage
                        addLocalNote("!!!!!!!!!!!!!!!!!PRP MESSAGE HAVEN'T BEEN SENT!!!!!!!!!!!!!!!!!")
                        localStorage.site = 1;
                        
                        window.open("about:blank","_self").close();
                    } 
                }

                window.addEventListener("message",handler,false);
            }else{
                // the logout will go back to home page, so below codes no need to put in else
                index++;
                if(index == 30){
                    // login with another account, identify this as fail. Downtime case4!
                    window.clearInterval(checkInterval);
                    if(localStorage.failNo == 2){
                        localStorage.failType = 4;
                    }
                    localStorage.failNo++;
                    getTime();
                    location.href = "https://partner.hpe.com/login";
                }
            }
        },1000)

        function logout(){
            jQuery('.user-dockbar-info').find('.link-arrow').click();
            jQuery('.sign_out').find('a')[0].click();
        }
    }


    // ******************   SEND EMAIL    ***************** 
    if(sendMailPHP){
        console.log('email page');
        // localStorage.logID = 0;

        window.setTimeout(function(){
            console.log('check service')

            // if(localStorage.logFile){
            //     openNew(localStorage.logFile);
            // }else{
                openNew()
            // }
        },testTime)
        // },900000)
    }

    // *****************************    OPENNEW     ********************************
    //  check server down. Downtime case 1!
    var serverIndex = 0;

    function openNew(logFileMsg){

        // if(!sendMailPHP){
        //     localStorage.system = 'PRP';
        // }
        
        console.log(serverIndex)
        if(serverIndex == 3){
            serverIndex = 0;
            localStorage.failType = 1;
            triggerEmail('error');
            return;
        }

        var k =0;
        var myPopup = window.open('https://partner.hpe.com/web/public/login');
        // var myPopup = window.open('http://16.202.11.196:8014/Test/error503.php');
        var t = new Date().getTime();
        var postMessageInterval = window.setInterval(function(){
            k++;
            if(k == 30){
                serverIndex++;
                getTime(serverIndex);
                window.clearInterval(postMessageInterval);
                // if(logFileMsg){
                //     openNew(logFileMsg);
                // }else{
                    openNew();
                // }
                
            }

            console.log('post message: ' + k)
            // if(logFileMsg){
            //     myPopup.postMessage(logFileMsg,'https://partner.hpe.com/group/upp-apj');
            // }else{
                // myPopup.postMessage(t,'https://partner.hpe.com/group/upp-apj');
                myPopup.postMessage(t,'https://partner.hpe.com');
                // myPopup.postMessage(t,'http://16.202.11.196:8014/Test/error503.php');
            // }
        },1000);

        window.addEventListener('message',function(event) {
            if(event.data == 'MessagePosted'){
                localStorage.site = 0;
                localStorage.overSite = 0;
                console.log('Message back!')
                // Build Listener
                window.clearInterval(postMessageInterval);
                // if(logFileMsg){
                //     localStorage.logFile = '';
                // }
                
                window.open("about:blank","_self").close();
            }
            // else if(event.data == 'Gateway_Timeout'){
            //     // Gateway_Timeout
            //     serverIndex++;
            //     getTime(serverIndex);
            //     window.clearInterval(postMessageInterval);
            //     if(logFileMsg){
            //         openNew(logFileMsg);
            //     }else{
            //         openNew();
            //     }
            // }else if(event.data == 'Service_Unavailable'){
            //     // Service_Unavailable

            // }
        },false);
    }

    function sendEmail(type,down){

        console.log('send email');
        console.log(type)
        console.log(down)

        if(down == 'false'){
            localStorage.down = true;
        }else if(down == 'true'){
            localStorage.down = false;
        }

         var toList = 'gechen.wang@hpe.com;';

        var errorSubject = '<Alert> PRP logins have failed';
        var errorContent = 
        '<div>'+
        '<div>Dear Portal Admin,</div>'+
        '<div><br>Logins to PRP have failed. Please validate Portal availability and take actions accordingly.</div>'+
        '<ul>'+
        '<li>1st fail: '+ localStorage.failTime1 + ' SGT</li>'+
        '<li>2nd fail: '+ localStorage.failTime2 + ' SGT</li>'+
        '<li>3th fail: '+ localStorage.failTime3 + ' SGT</li>'+
        '</ul>'+
        '<div>Please note that this email is generated automatically. Do not reply to this message.</div>'+
        '<div>'+
        '<br>Regards,<br><br>Digital Experience & Communications team'+
        '</div>'+
        '</div>';

        var recoverSubject = '<Alert> PRP logins have recovered';
        var recoverContent = 
        '<div>'+
        '<div>Dear Portal Admin,</div>'+
        '<div><br>The Portal is now working correctly. We will continue to monitor availability.</div>'+
        '<div><br>Please note that this email is generated automatically. Do not reply to this message.</div>'+
        '<div>'+
        '<br>Regards,<br><br>Digital Experience & Communications team'+
        '</div>'+
        '</div>';
        
        var message, subject;
        if(type == 'recover'){
            message = recoverContent;
            subject = recoverSubject;
        }else if(type == 'error'){
            message = errorContent;
            subject = errorSubject;
        }

        // console.log(message);

        localStorage.failNo = 0;
        localStorage.failTime1 = 0;
        localStorage.failTime2 = 0;
        localStorage.failTime3 = 0;
        localStorage.failType = 0;
        
        var formDiv = 
        '<form action="http://16.202.11.196:8014/Services/SendMail.php" method="post" name="emailForm" id="emailSubmit">'+
        '<input type="text" name="strOption" value="SendMail">'+
        '<input type="text" name="emailAccount" value="partnerportal.support@hpe.com">'+
        '<input type="text" name="subject" value="'+subject+'">'+
        '<input type="text" name="toList" value="'+toList+'">'+
        '<input type="text" name="Message" value="'+message+'">'+
        '<input type="text" name="type" value="'+type+'">'+
        '</form>';
        // console.log(formDiv);
        jQuery('body').append(formDiv);
        jQuery('#emailSubmit').submit(); 
    }


    // **********************   RESET   **************************
    function reset(){
        console.log('15mins waiting');
        localStorage.failNo = 0;
        localStorage.failTime1 = 0;
        localStorage.failTime2 = 0;
        localStorage.failTime3 = 0;
        localStorage.failType = 0;
        localStorage.overSite = 0;
        // if(!sendMailPHP){
        //     localStorage.system = 'DXP';
        // }

        window.setTimeout(function(){
            // console.log('check service');
            // window.removeEventListener('message',handler,false);
            // if(sendMailPHP && localStorage.logFile){
            //     openNew(localStorage.logFile)
            // }else{
                openNew();
            // }
        },testTime)
        // },900000)
    }

    // **********************   TRIGGER EMAIL   ************************** 
    var uploadIndex = 0;
    function triggerEmail(type){

        if(!sendMailPHP){
            uploadTime(uploadIndex);
        }
        
        if(type == 'error'){
            if(localStorage.down == 'false'){
                // error email
                AddLog(type,1);
                sendEmail('error','false');
            }else{
                AddLog(type,0);
                reset();
            }
        }else if(type == 'recover'){
            if(localStorage.down == 'true'){
                // recover email
                AddLog(type,1);
                sendEmail('recover','true');
            }else{
                AddLog(type,0);
                reset();
            }
        }
    }

    
    function uploadTime(index){

        // if(index < 2){
            var date = new Date();
            var localTime = date.getTime();
            var localOffset=date.getTimezoneOffset()*60000; 
            var utc = localTime + localOffset;
            offset =8;
            var SGT = utc + (3600000*offset);
            var time = new Date(SGT).toLocaleString();
            
            // console.log(SGT)
            // console.log(time)
            jQuery.ajax({
                type: "POST",
                url: "https://hpe-rfb.itcs.hpe.com/form/views/2612/data/update",
                dataType: 'json',
                data: {
                    EntryId:1,
                    SGT:SGT,
                    TimeString:time
                },
                success: function(data) {
                    console.log('Time upload success!');
                    console.log(data);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log(textStatus);
                    // console.log('uploadIndex:' + uploadIndex);
                    // uploadIndex++;
                    // uploadTime(uploadIndex);
                },
            })
        // }else{
        //     uploadIndex = 0;
        // }
    }


    function getTime(serverIndex){

        var date = new Date();
        var localTime = date.getTime();
        var localOffset=date.getTimezoneOffset()*60000; 
        var utc = localTime + localOffset;
        offset =8;
        var SGT = utc + (3600000*offset);
        var time = new Date(SGT).toLocaleString();
        
        // var month = date.getMonth() + 1;
        // var day = date.getDate();
        // var year = date.getFullYear();
        // var HMS = date.toLocaleTimeString()
        // var time = month +'/'+ day +'/'+ year +' '+ HMS; 

        if(serverIndex){
            switch(serverIndex){
                case 1:
                localStorage.failTime1 = time;
                break;

                case 2:
                localStorage.failTime2 = time;
                break;

                case 3:
                localStorage.failTime3 = time;
                break;
            }
        }else{
            switch(parseInt(localStorage.failNo)){
                case 1:
                localStorage.failTime1 = time;
                break;
        
                case 2:
                localStorage.failTime2 = time;
                break;
        
                case 3:
                localStorage.failTime3 = time;
                break;
            }
        }

        console.log(localStorage.failTime1)
        console.log(localStorage.failTime2)
        console.log(localStorage.failTime3)
    }

    

    function AddLog(type,emailTrigger){
        
        if(type == 'recover'){
            type = 1;
        }else if(type == 'error'){
            type = 0;
        }
        
    
        // LogID LogTime LogStatus EamilTrigger LogFailType LogFailTime1 LogFailTime2 LogFailTime3
        // LogStatus:   1:Success    0:Fail
        // EamilTrigger:    1:Yes   0:No
        // LogFailType:     0:N/A   1: Portal Not Available 2:Login Page Load Fail  3:Demo Account Login Fail   4:Homepage Load Fail
        // LogFailTime:     0:N/A   

        // eg: 1%7/9/2019, 4:08:05 PM%1%0%0%0%0%0*
        // LogID % LogTime % LogStatus % EamilTrigger % LogFailType % 3failtime


        localStorage.logID++;

        if(localStorage.logFile == undefined){
            localStorage.logFile = '';
        }

        localStorage.logFile += localStorage.logID +'%'; // LogID
        localStorage.logFile += getCurrentTime() +'%'; // LogTime
        if(type == 1 && emailTrigger == 0 && localStorage.failType == 0 && localStorage.failTime1 == 0 && localStorage.failTime2 == 0 &&localStorage.failTime3 == 0){
            localStorage.logFile += 'S*';
        }else{
            localStorage.logFile += type+'%'; // LogStatus
            localStorage.logFile += emailTrigger+'%'; // EamilTrigger
            localStorage.logFile += localStorage.failType+'%'; //LogFailType
            localStorage.logFile += localStorage.failTime1+'%';
            localStorage.logFile += localStorage.failTime2+'%';
            localStorage.logFile += localStorage.failTime3+'*';
        }
    }

    function mergeLogFile(msg){
        console.log('mergeLogFile')
        console.log(msg)
        
        var result = msg.split('*');
        var len = result.length-1;

        var tempStr,tempNum;
        for(var i =1;i<result.length;i++){
            tempNum = parseInt(localStorage.logID) + i;
            tempStr = tempNum + result[i-1].substr(1) + '*';
            localStorage.logFile += tempStr;
        }

        localStorage.logID = parseInt(localStorage.logID) + len;
        
    }
    

    function checkSite(){
        console.log('check site');
        console.log('site No:' + localStorage.site)
        if(localStorage.site == 0){
            localStorage.site = 1;
        }else if(localStorage.site == 1){
            localStorage.site = 2;
        }else if(localStorage.site == 2){
            if(localStorage.overSite < 2){
                addLocalNote('/checkSite2!!overSite:' +  localStorage.overSite + '!!')
                localStorage.overSite++;
                window.open("about:blank","_self").close();
            }else{
                // 如果localStorage.overSite = 2，说明连续三次openNew都是localStorage为2然后关闭了,这次不执行关闭
                localStorage.overSite = 0;
                addLocalNote('/连续三次openNew时site为2')
            }
        }else{
            addLocalNote('/checkSiteElse:')

            window.open("about:blank","_self").close();
        }
    }   
    
}
