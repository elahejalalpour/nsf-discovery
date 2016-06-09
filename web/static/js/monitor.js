$(function() {
	"use strict";
	console.log("Execution begins in monitor.js");
	
	var model = monitor.model();
	var map = new Object();
	$("body").prepend("<h1>VNF Management System</h1>");
	function repeat() {
		//repeat every 2 seconds
		setTimeout(repeat, 2000);
		$("#Hosts").empty();
		
		model.getData("Host");
		var hosts = model.getHost();
		//console.log(hosts)
		//add host entries
		for(var i = 0; i < hosts.length; i++) {
			//console.log(hosts[i]);
			var hostname = hosts[i]['Host_name'];
			var IP = hosts[i]['Host_ip'];
			var cpu = hosts[i]['Host_cpu'];
			var ram = Math.round(hosts[i]['Host_used_mem']/hosts[i]['Host_total_mem']*100);
			var active = hosts[i]['Active'];
			var result = "<li class='Host " + hostname + "'>";
			result+="<h2>"+hostname+"</h3>";
			result+="<p class='IP'>IP: "+IP+"</p>";
			result+="<p style='width:100%' data-value='"+cpu+"'>CPU</p>";
			result+="<progress max='100' value='"+cpu+"' class='html5'>";
			result+=`<div class='progress-bar'>
							<span style='width: 80%'>80%</span>
						</div>
						</progress>`;
			result+="<p style='width:100%' data-value='"+ram+"'>RAM</p>";
			result+="<progress max='100' value='"+ram+"' class='html5'>";
			result+=`<div class='progress-bar'>
							<span style='width: 80%'>80%</span>
						</div>
						</progress>`;
			if (active) {
				result+="<p>Status:"+"<span style='color:green'> Running</span></p>"
				//add show VNF
				result+="<button id="+hostname+"_button class='mybutton'>Show VNFS</button>";
				//add start button
				result+="<button id="+hostname+"_start class='mybutton'>Start All</button>";
				//add stop button
				result+="<button id="+hostname+"_stop class='mybutton'>Stop All</button>";
				
				result+="</li>";
				$('#Hosts').append(result);
				
				//add show listener
				$("#"+hostname+"_button")[0].addEventListener('click', function () {
					var host = this.id.split("_")[0];
					if (map[host] === true) map[host] = false;
					else map[host] = true;
				});
				//add start all listener
				$("#"+hostname+"_start")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],'*',args[1]);
				});
				//add stop all listener
				$("#"+hostname+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],'*',args[1]);
				});
			} else {
				result+="<p>Status:"+"<span style='color:red'> Inactive</span></p>"
				result+="</li>";
				$('#Hosts').append(result);
			}
			if (map[hostname]) {
				$('.'+hostname).append("<div class="+hostname+"_vnfs></div>");
			}
		}
		model.getData("VNF");
		var vnfs = model.getVnf();
		//add VNF entries
		for(var i = 0; i < vnfs.length; i++) {
			var hostname = vnfs[i]['Host_name']
			if(map[hostname]) {
				//console.log(vnfs[i]);
				var id = vnfs[i]['Con_id'];
				var vnfname = vnfs[i]['Con_name'];
				var IP = vnfs[i]['VNF_ip'];
				var status = vnfs[i]['VNF_status'];
				var type = vnfs[i]['VNF_type'];
				$("."+hostname+id).remove();
				$("."+hostname).append("<div class="+"'"+hostname+id+"'>\n</div>");
				var result = "";
				result+=`<p> <span style='font-weight: bold; font-size: 10pt'> 
							Container ID: </span>`+id.substring(0,11);
				result+=`<span style='font-weight: bold; 
							font-size: 10pt'> Name: </span>`+vnfname+"</p>";
				result+="<p> <span style='font-weight: bold; font-size: 10pt'> IP: </span>"+IP;
				result+=`<span style='font-weight: bold; 
							font-size: 10pt'> Status: </span>`+status;
				result+=`<span style='font-weight: bold; 
							font-size: 10pt'> Type: </span>`+type+"</p>";
				$("."+hostname+id).append(result);
				//add start button
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_start>Start</button>")
				$("#"+hostname+"_"+id+"_start")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
				//add stop button
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_stop>Stop</button>")
				$("#"+hostname+"_"+id+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
				//add destroy button
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_destroy>Destroy</button>")
				$("#"+hostname+"_"+id+"_destroy")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
			}
		}
	}
	repeat()
	
});
