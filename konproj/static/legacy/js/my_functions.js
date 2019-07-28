/* creator: michelepasin */


/*** Temporary text filler function. Remove when deploying template. ***/
var gibberish=["This is just some filler text", "Sometimes some gibberish may mean more than what you think", "Amore non amato amar perdona"]
function filltext(words){
	var output = "";
	for (var i=0; i<words; i++) 
		output = output + (gibberish[Math.floor(Math.random()*3)]+" ");
		return output;
}

function addGibberish(number, location) {
	var stuff = filltext(number);
	$(location).empty().append(stuff);
}


/*
generic functions for jquery operations
*/

function updateDiv(divname, ajaxcall) {
    $.get(ajaxcall,
   		 { },
              function(data){
                 $("#" + divname).append(data);
              }
   );  
}

function clear_and_updateDiv(divname, ajaxcall) {
    $.get(ajaxcall,
   		 { },
              function(data){
                 $("#" + divname).empty().append(data);
              }
   );  
}





function startXmlImport(div1, div2) {
	
	$("#" + div1).empty().append("Loading... please wait...")
	
    $.get('import_xml',
   		 { },
              function(data){
                 $("#" + div1).empty().append(data);
              }
   );  
}

/*functions for showing continuously the contents of the log
*/

function show_log(div2) {
	//$("#" + div2).empty().append("Loading... please wait...")
    $.get('show_log',
      		 { },
                 function(data){
                    $("#" + div2).append(data);
                 }
      ); 
}    
   
function stop_log(div) {
	clearInterval ( myIntervalId );
 
    $.get('stop_log',
      		 { },
                 function(data){
                    $("#" + div).empty().append(data);
                 }
      ); 
} 

//functions for cyclical update   ----> http://www.elated.com/articles/javascript-timers-with-settimeout-and-setinterval/

var myIntervalId = 0;

function myClickHandler(location)
{
	 
  if (true)
  {
	  $("#" + location).empty();
    // Start the timer
	  txt = "show_log('" + location + "')"
	  myIntervalId = setInterval ( txt , 1000 );
  }
  else
  {
    clearInterval ( myIntervalId );
  }
}



///end



function create_dbtables(div) {

	$("#" + div).empty().append("Loading... please wait...")
    $.get('create_dbtables',
      		 { },
                 function(data){
                    $("#" + div).empty().append(data);
                 }
      );
	
}










/*old functions to check*/


/*
function for editing elements*/

function editElement(selection) {
	loadingData = "<h6>Getting ready to edit element... " + selection + "</h6>";
	$("div.dump2").empty().append(loadingData);
		
     $.get("ModsEditor",
             { key: selection },
               function(data){
                  $("div.dump2").empty().append(data);
               }
    );
     
    document.getElementById('main_tab_section').tabber.tabShow(1);
    
}



/*
function for viewing elements*/

function viewElement(selection) {
	loadingData = "<h6>Getting ready to view element... " + selection + "</h6>";
	$("div.dump3").empty().append(loadingData);
		
     $.get("viewItemCopy.jsp",
             { key: selection },
               function(data){
                  $("div.dump3").empty().append(data);
               }
    );
     
    document.getElementById('main_tab_section').tabber.tabShow(2);
    
}


function viewElementMods(selection) {
	loadingData = "<h6>Getting ready to view (mods-only) element... " + selection + "</h6>";
	$("div.dump4").empty().append(loadingData);
		
     $.get("viewModsItemCopy.jsp?",
             { key: selection },
               function(data){
                  $("div.dump4").empty().append(data);
               }
    );
     
    document.getElementById('main_tab_section').tabber.tabShow(3);
    
}


