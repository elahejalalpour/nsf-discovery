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
			console.log(hosts[i]);
			console.log(hosts[i]['Host_name']);
			var hostname = hosts[i]['Host_name'];
			var IP = hosts[i]['Host_ip'];
			var cpu = hosts[i]['Host_cpu'];
			var ram = Math.round(hosts[i]['Host_used_mem']/hosts[i]['Host_total_mem']*100);
			var active = hosts[i]['Active'];
			$("."+hostname).remove();
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
