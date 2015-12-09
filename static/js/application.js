var first_inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");

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


var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/key_down");
outbox.onopen = function() {
    outbox.send("lalaa");
};
outbox.onclose = function(){
    console.log('outbox closed');
    this.outbox = new WebSocket(outbox.url);
};

var targetElement = document.body;

function getArrowKeyDirection (keyCode) {
  return {
    37: 'left',
    39: 'right',
    38: 'up',
    40: 'down'
  }[keyCode];
}

function isArrowKey (keyCode) {
  return !!getArrowKeyDirection(keyCode);
}

targetElement.addEventListener('keydown', function (event) {
    var direction, keyCode = event.keyCode;
    if (isArrowKey(keyCode)) {
        direction = getArrowKeyDirection(keyCode);
        outbox.send(direction);
    }
});