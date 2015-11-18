var inbox = new ReconnectingWebSocket("ws://"+ location.host + "/receive");
var outbox = new ReconnectingWebSocket("ws://"+ location.host + "/submit");

function hexToBase64(str) {
    return btoa(String.fromCharCode.apply(null, str.replace(/\r|\n/g, "").replace(/([\da-fA-F]{2}) ?/g, "0x$1 ").replace(/ +$/, "").split(" ")));
}

inbox.onmessage = function(message) {
    if (message) {
        var base_64_frame = message.data;
        $("#cam").attr("src", "data:image/jpg;base64, " + base_64_frame);
    }
};

inbox.onclose = function(){
    console.log('inbox closed');
    this.inbox = new WebSocket(inbox.url);

};

outbox.onclose = function(){
    console.log('outbox closed');
    this.outbox = new WebSocket(outbox.url);
};

$("#input-form").on("submit", function(event) {
  event.preventDefault();
  var handle = $("#input-handle")[0].value;
  var text   = $("#input-text")[0].value;
  outbox.send(JSON.stringify({ handle: handle, text: text }));
  $("#input-text")[0].value = "";
});
