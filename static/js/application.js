var first_inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");

first_inbox.onmessage = function(message) {
    if (message) {
        var base_64_frame = message.data;
        $("#cam").attr("src", "data:image/jpg;base64, " + base_64_frame);
    }
};

first_inbox.onclose = function(){
    console.log('inbox closed');
    this.first_inbox = new WebSocket(first_inbox.url);

};


outbox.onclose = function(){
    console.log('outbox closed');
    this.outbox = new WebSocket(outbox.url);
};


//Second camera

var second_inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive_second");


second_inbox.onmessage = function(message) {
    if (message) {
        var base_64_frame = message.data;
        $("#cam2").attr("src", "data:image/jpg;base64, " + base_64_frame);
    }
};

second_inbox.onclose = function(){
    console.log('inbox closed');
    this.second_inbox = new WebSocket(second_inbox.url);

};