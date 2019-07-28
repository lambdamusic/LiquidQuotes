// crunch the following using <http://ted.mielczarek.org/code/mozilla/bookmarklet.html>
// then you can use it as a bookmarklet that avoids the popup error
// 

// URL testing: http://127.0.0.1:8000/new/addonthefly/
// URL online: http://www.LiquidQuotes.com/new/addonthefly/

javascript:(function(){
	var POPUP_URL = "http://127.0.0.1:8000/new/addonthefly/";
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
	var url=encodeURIComponent(location.href);
	var title=encodeURIComponent(document.title);
	// if you want to open a pop up
	window.open( POPUP_URL + "?text=" + text + "&url=" + url + "&title=" + title, "myWindow", 
	"status = 1, height = 500, width = 650, resizable = 0" );
})();

