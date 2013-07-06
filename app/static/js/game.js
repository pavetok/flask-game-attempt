var CANVAS_WIDTH = 480;
var CANVAS_HEIGHT = 320;

var canvasElement = $("<canvas width='" + CANVAS_WIDTH +
    "' height='" + CANVAS_HEIGHT + "'></canvas>");
var ctx = canvasElement.get(0).getContext("2d");
canvasElement.appendTo('body');

//var FPS = 30;
var FPS = 5;
setInterval(function() {
    update();
}, 1000/FPS);

function draw(objects) {
    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    for (var name in objects) {
        if (objects.hasOwnProperty(name)) {
            var obj = objects[name];
            //draw a rectangle
//            ctx.fillRect(obj['x'], obj['y'], obj['size'], obj['size']);
            // draw a name
            ctx.fillStyle = "#000"; // Set color to black
            ctx.fillText(name, obj['x'] - 5, obj['y'] - 3);
            //draw a circle
            ctx.fillStyle = 'green';
            ctx.beginPath();
            ctx.arc(
                obj['x'] + (obj['size'] / 2),
                obj['y'] + (obj['size'] / 2),
                obj['size'] / 2,
                0, Math.PI*2, false);
            ctx.closePath();
            ctx.fill();
        }
    }
}

function update() {
    $.getJSON('/update', function() {
        console.log( "success" );
    })
        .done(function(objects) {
            draw(objects);
        })
        .fail(function() {
            console.log("Error: Could not contact server");
        });
}