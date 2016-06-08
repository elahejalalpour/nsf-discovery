$(function() {
	"use strict";
	console.log("Execution begins in monitor.js");
	
	var model = monitor.model();
	var map = new Object();
	 
	function repeat() {
		//repeat every 2 seconds
		setTimeout(repeat, 2000);
		$("body").empty();
		$("body").prepend("<h1>VNF Management System</h1>");
		model.getData("Host");
		var hosts = model.getHost();
		//console.log(hosts)
		$("br").remove()
		//add host entries
		for(var i = 0; i < hosts.length; i++) {
			//console.log(hosts[i]);
			var hostname = hosts[i][0];
			var IP = hosts[i][1];
			var cpu = hosts[i][2];
			var ram = Math.round(hosts[i][5]/hosts[i][3]*100);
			var active = hosts[i][7];
			$("."+hosts[i][0]).remove();
			$("body").append("<div class="+"'"+hostname+"'>\n</div>");
			$("."+hostname).append("Host: "+hostname+" IP: "+IP
											+" CPU: "+cpu+"%"+" RAM: "+ram+"% ");
			if(active === 0) {
				$("."+hostname).append("<span style='color:red'>-Host Inactive- </span>");
				map[hostname] = false;
			} else {
				$("."+hostname).append("<span style='color:green'>-Host Online- </span>");
				map[hostname] = true;
				//add start button
				$("."+hostname).append("<button id="+hostname+"_start>Start All</button>")
				$("#"+hostname+"_start")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],'*',args[1]);
				});
				//add stop button
				$("."+hostname).append("<button id="+hostname+"_stop>Stop All</button>")
				$("#"+hostname+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],'*',args[1]);
				});
			}
			
			$("body").append("<br></br>");
		}
		
		model.getData("VNF");
		var vnfs = model.getVnf();
		//add VNF entries
		for(var i = 0; i < vnfs.length; i++) {
			var hostname = vnfs[i][2]
			if(map[hostname]) {
				//console.log(vnfs[i]);
				var id = vnfs[i][0];
				var vnfname = vnfs[i][1];
				var IP = vnfs[i][3];
				var status = vnfs[i][4];
				var type = vnfs[i][5];
				$("."+hostname+id).remove();
				$("."+hostname).append("<div class="+"'"+hostname+id+"'>\n</div>");
				$("."+hostname+id).append("Container ID: "+id.substring(0,11)+" Name: "+vnfname
												+" IP: "+IP+" Status: "
												+status+" Type: "+type+"\n");
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
