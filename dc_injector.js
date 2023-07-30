(function() {
    'use strict';
    var first = true;
    var msgId = 1;
    var lastId = "";
    var observer = null;
    var lastPathname = "";

    function htmlToElement(html) {
        const parser = new DOMParser();
        const htmlDocument = parser.parseFromString(html, "text/html");
        return htmlDocument.body.firstChild          
    }

    const callback = function (records, observer) {
        if (first) {
            first = false;
            return;
        }

        var ele = document.querySelectorAll('li[id^=chat-messages-]');
        var last = ele[ele.length - 1];
        
        var newMsgId = last.querySelector('div[id^=message-content-]:not([class*="isSending-"]').id
        var userName = last.querySelector('span[class^=username-]').innerText
        
        if (last.innerText !== "" && lastId !== newMsgId) {
            console.log(last.innerHTML);
            lastId = newMsgId;
            var ts = parseInt(newMsgId.substr(16));
            var unixTime = parseInt(ts/4194304+(1420070400000)); // convert snowflake to unixtime (in ms)
            var utcTime = (new Date(unixTime)).toISOString();
            var utcOffset = (new Date()).getTimezoneOffset()*60*1000;                
            var localTime = (new Date(unixTime-utcOffset)).toISOString().replace("Z","");                
            var html = `<div id="chat-stack-id-${msgId}" data-msgId="${newMsgId}" data-utcTime="${utcTime}" data-localTime="${localTime}" data-unixTime="${unixTime}" data-userName="${userName}">${last.innerText}</div>`;
            //console.log(html);
            var div = htmlToElement(html);
            var parentNode = document.querySelector('body');
            parentNode.appendChild(div);
            msgId += 1;
        }
    };

    var loop = setInterval(function (ele) {
        var newPathname = location.pathname;      	
        if(newPathname !== lastPathname) {
            lastPathname = newPathname;
            if(observer != null) {
                observer.disconnect();
                observer = null;
            }
        }
        
        if(observer == null) {        		
            var node = document.querySelector('div[class^=messagesWrapper-]');        	
            if (node == null) {
                console.log("Nothing Found")
                return;
            }
            observer = new MutationObserver(callback);
            observer.observe(node, { attributes: true, childList: true, subtree: true })
            console.log("attached to messageWrapper");
        }      
    },1000);
})();