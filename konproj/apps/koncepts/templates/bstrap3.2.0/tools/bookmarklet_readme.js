// crunch the following using <http://ted.mielczarek.org/code/mozilla/bookmarklet.html>
// then you can use it as a bookmarklet that avoids the popup error
// 

// URL testing: http://127.0.0.1:8000/new/addonthefly/
// URL online: http://www.LiquidQuotes.com/new/addonthefly/
// URL online: http://koncepts.michelepasin.org/new/addonthefly/
// URL online: http://stg.LiquidQuotes.com/new/addonthefly/

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




October 30, 2013:
---------------------------------

javascript:(function()%7Bjavascript:(function()%7Bvar POPUP_URL%3D"http://stg.LiquidQuotes.com/new/addonthefly/"%3Bvar text%3Btry%7Btext%3D((window.getSelection%26%26window.getSelection())%7C%7C(document.getSelection%26%26document.getSelection())%7C%7C(document.selection%26%26document.selection.createRange%26%26document.selection.createRange().text))%3B%7Dcatch(e)%7Btext%3D""%3B%7Dvar url%3DencodeURIComponent(location.href)%3Bvar title%3DencodeURIComponent(document.title)%3Bwindow.open(POPUP_URL%2B"%3Ftext%3D"%2Btext%2B"%26url%3D"%2Burl%2B"%26title%3D"%2Btitle,"myWindow","status %3D 1, height %3D 500, width %3D 650, resizable %3D 0")%3B%7D)()%3B%7D)()%3B


PS: make sure the url contains the scheme (http://) !









OTHER ATTEMPTS
---------------------------------



2014-03-04 (tried removing title bar but not possible! http://stackoverflow.com/questions/16603308/hiding-address-bar-in-all-browsers)
---------------------------------

javascript:(function()%7Bjavascript:(function()%7Bvar POPUP_URL%3D"http://stg.LiquidQuotes.com/new/addonthefly/"%3Bvar text%3Btry%7Btext%3D((window.getSelection%26%26window.getSelection())%7C%7C(document.getSelection%26%26document.getSelection())%7C%7C(document.selection%26%26document.selection.createRange%26%26document.selection.createRange().text))%3B%7Dcatch(e)%7Btext%3D""%3B%7Dvar url%3DencodeURIComponent(location.href)%3Bvar title%3DencodeURIComponent(document.title)%3Bwindow.open(POPUP_URL%2B"%3Ftext%3D"%2Btext%2B"%26url%3D"%2Burl%2B"%26title%3D"%2Btitle,"myWindow","status %3D 0, height %3D 500, width %3D 650, resizable %3D 0, titlebar %3D 0, toolbar %3D 0, location %3D 0")%3B%7D)()%3B%7D)()%3B