// create the element:
var $e = $('<div id="yourelement"></div>');

// append it to the body:
$('body').append($e);

// style it:
$e.css({
    position: 'absolute',
    top: '10px',
    right: '10px',
    width: '200px',
    height: '90px',
    backgroundColor: 'red'
});