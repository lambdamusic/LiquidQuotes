// FIRST ATTEMPT: NOT USED

// this is the second part of a two-files version of the bookmarklet
// call this file via a bookmarklet that does this:
// drawback: browsers will block the popup!
// 
// javascript:(function(){
//   _my_script=document.createElement('SCRIPT');
//   _my_script.type='text/javascript';
//   _my_script.src='http://127.0.0.1:8000/dj_app_media/koncepts/js/popup.js?';
//   document.getElementsByTagName('head')[0].appendChild(_my_script);
// })();


var POPUP_URL = "http://127.0.0.1:8000/addonthespot/"


// get the currently selected text
 var text;
 try {
   text= ((window.getSelection && window.getSelection()) ||
	(document.getSelection && document.getSelection()) ||
	(document.selection &&
	document.selection.createRange &&
	document.selection.createRange().text));
 }
 catch(e){ // access denied on https sites
   text = "";
 }


// javascript:location.href='http://del.icio.us/post?v=4;
var url=encodeURIComponent(location.href);
var title=encodeURIComponent(document.title);


// 
// alert("URL : " + title + "\nTITLE" + url + "\n\n " + text);
// 



// if you want to open a pop up
function myPopup2() {
window.open( POPUP_URL + "?text=" + text + "&url=" + url + "&title=" + title, "myWindow", 
"status = 1, height = 500, width = 750, resizable = 0" );

}

myPopup2();