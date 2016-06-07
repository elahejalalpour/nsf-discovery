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
			$("."+hosts[i][0]).remove();
			$("body").append("<div class="+"'"+hosts[i][0]+"'>\n</div>");
			$("."+hosts[i][0]).append("Host: "+hosts[i][0]+" IP: "+hosts[i][1]
											+" CPU: "+hosts[i][2]+"%"+" RAM: "
											+Math.round(hosts[i][5]/hosts[i][3]*100)+"% ");
			if(hosts[i][7] === 0) {
				$("."+hosts[i][0]).append("<span style='color:red'>-Host Inactive- </span>");
				map[hosts[i][0]] = false;
			} else {
				$("."+hosts[i][0]).append("<span style='color:green'>-Host Online- </span>");
				map[hosts[i][0]] = true;
			}
			//add start button
			$("."+hosts[i][0]).append("<button id="+hosts[i][0]+"_start>Start All</button>")
			$("#"+hosts[i][0]+"_start")[0].addEventListener('click', function () {
				console.log(this.id);
				var args = this.id.split("_");
				model.makeReq(args[0],'*',args[1]);
			});
			//add stop button
			$("."+hosts[i][0]).append("<button id="+hosts[i][0]+"_stop>Stop All</button>")
			$("#"+hosts[i][0]+"_stop")[0].addEventListener('click', function () {
				console.log(this.id);
				var args = this.id.split("_");
				model.makeReq(args[0],'*',args[1]);
			});
			$("body").append("<br></br>");
		}
		
		model.getData("VNF");
		var vnfs = model.getVnf();
		//add VNF entries
		for(var i = 0; i < vnfs.length; i++) {
			if(map[vnfs[i][2]]) {
				//console.log(vnfs[i]);
				var id = vnfs[i][0];
				var name = vnfs[i][1];
				var host = vnfs[i][2];
				$("."+host+id).remove();
				$("."+host).append("<div class="+"'"+host+id+"'>\n</div>");
				$("."+host+id).append("Container ID: "+id.substring(0,11)+" Name: "+name
												+" IP: "+vnfs[i][3]+" Status: "
												+vnfs[i][4]+" Type: "+vnfs[i][5]+"\n");
				//add start button
				$("."+host+id).append("<button id="+host+"_"+id+"_start>Start</button>")
				$("#"+host+"_"+id+"_start")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
				//add stop button
				$("."+host+id).append("<button id="+host+"_"+id+"_stop>Stop</button>")
				$("#"+host+"_"+id+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
				//add destroy button
				$("."+host+id).append("<button id="+host+"_"+id+"_destroy>Destroy</button>")
				$("#"+host+"_"+id+"_destroy")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2]);
				});
			}
		}
	}
	repeat()
	
});
