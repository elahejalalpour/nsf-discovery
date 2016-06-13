$(function() {
	"use strict";
	console.log("Execution begins in monitor.js");
	
	var model = monitor.model();
	var map = new Object();
	//$("body").prepend("<h1>VNF Management System</h1>");
	//add listener to left panel
	$("#navi-hosts")[0].addEventListener('click', function () {
			$("a").removeClass('active');
			$("#navi-hosts").addClass('active');
			$('#VNFS').prop('hidden', 'hidden');
			$('#Chain').prop('hidden', 'hidden');
			$('#Hosts').removeProp('hidden');
	});
	
	$("#navi-vnfs")[0].addEventListener('click', function () {
			$("a").removeClass('active');
			$("#navi-vnfs").addClass('active');
			$('#Hosts').prop('hidden', 'hidden');
			$('#Chain').prop('hidden', 'hidden');
			$('#VNFS').removeProp('hidden');
	});
	
	$("#navi-chain")[0].addEventListener('click', function () {
			$("a").removeClass('active');
			$("#navi-chain").addClass('active');
			$('#Hosts').prop('hidden', 'hidden');
			$('#VNFS').prop('hidden', 'hidden');
			$('#Chain').removeProp('hidden');
	});
	
	
	function repeat() {
		//repeat every 2 seconds
		setTimeout(repeat, 2000);
		$("#Hosts").empty();
		$("#VNFS").empty();
		$("#Chain").empty();
		
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
			var result = "<li class='progli Host " + hostname + "'>";
			if (!active) {
				cpu = 0;
				ram = 0;
			}
			result+="<h2>"+hostname+"</h2>";
			result+="<p class='IP'>IP: "+IP+"</p>";
			result+="<p style='width:100%' data-value='"+cpu+"'>CPU</p>";
			result+="<progress max='100' value='"+cpu+"' class='css3'>";
			result+=`<div class='progress-bar'>
							<span style='width: 80%'>80%</span>
						</div>
						</progress>`;
			result+="<p style='width:100%' data-value='"+ram+"'>RAM</p>";
			result+="<progress max='100' value='"+ram+"' class='css3'>";
			result+=`<div class='progress-bar'>
							<span style='width: 80%'>80%</span>
						</div>
						</progress>`;
			if (active) {
				result+="<p>Status:"+"<span style='color:green'> Running</span></p>"
				//add show VNF
				if (map[hostname]) {
					result+="<button id="+hostname+"_button class='mybutton'>Hide VNFS</button>";
				} else {
					result+="<button id="+hostname+"_button class='mybutton'>Show VNFS</button>";
				}
				//add start button
				result+="<button id="+hostname+"_start class='mybutton'>Start All</button>";
				//add stop button
				result+="<button id="+hostname+"_stop class='mybutton'>Stop All</button>";
				
				result+="</li>";
				$('#VNFS').append(result);
				
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
				map[hostname] =false;
				result+="<p>Status:"+"<span style='color:red'> Inactive</span></p>"
				result+="</li>";
				$('#VNFS').append(result);
			}
			if (map[hostname]) {
				$('.'+hostname).append("<div class="+hostname+"_vnfs></div>");
			} 
		}
		//Hosts tab
		for(var i = 0; i < hosts.length; i++) {
			var hostname = hosts[i]['Host_name'];
			var IP = hosts[i]['Host_ip'];
			var cpu = hosts[i]['Host_cpu'];
			var ram = Math.round(hosts[i]['Host_used_mem']/hosts[i]['Host_total_mem']*100);
			var active = hosts[i]['Active'];
			var cpus = hosts[i]['cpus'];
			var result = "<li class='progli Host " + hostname + "'>";
			var network = hosts[i]['network'];
			result+="<h2>"+hostname+"</h2>";
			result+="<p class='IP'>IP: "+IP+"</p>";
			if (active) {
				//cpu+ram
				result+="<p style='margin:0 0 1em'>Status:"+"<span style='color:green'> Running</span></p>"
				result+="<p style='width:100%;font-weight:bold' data-value='"
							+cpu+"'>CPU ("+cpus.length+" cores)</p>";
				result+="<progress max='100' value='"+cpu+"' class='css3'>";
				result+=`<div class='progress-bar'>
								<span style='width: 80%'>80%</span>
							</div>
							</progress>`;
				result+="<p style='font-size:8'> Cores:</p>";
							
				for(var j = 0; j < cpus.length; j++) {
					result+="<progress max='100' value='"+cpus[j]+"' class='css3' id='CPU'>";
					result+=`<div class='progress-bar'>
									<span style='width: 80%'>80%</span>
								</div>
								</progress>`;
				}
				result+="<br></br>"
				var total_ram = Math.round(hosts[i]['Host_total_mem']/1024/1024);
				var used_ram = Math.round(hosts[i]['Host_used_mem']/1024/1024);
				result+="<p style='width:100%;font-weight:bold' data-value='"
							+ram+"'>RAM (Total: "+
							total_ram+" MB &nbspUsed: "+used_ram+" MB)</p>";
				result+="<progress max='100' value='"+ram+"' class='css3'>";
				result+=`<div class='progress-bar'>
								<span style='width: 80%'>80%</span>
							</div>
							</progress>`;
				//network
				result+="<p style='font-weight:bold;margin:0.5em 0 0.2em 0'>Network</p>";
				result+=`<table id=network style="width:100%;font-size:10pt;">
							  <tr>
								 <th>Interface</th>
								 <th>Sent(Bytes)</th>
								 <th>Received(Bytes)</th>
							  </tr>`;
				for (var key in network) {
					result+='<tr><td>'+key+'</td>'
								+'<td>'+network[key][0]+'</td>'
								+'<td>'+network[key][1]+'</td>'+'</tr>';
				}
				result+="</table>";
				
			} else {
				result+="<p>Status:"+"<span style='color:red'> Inactive</span></p>"
			}
			
			result+="</li>";
			if ((i % 2) === 1) result+="<br></br><br></br><br></br>";
			$('#Hosts').append(result);
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
				$("."+hostname+"_vnfs").append("<div class="+"'"+hostname+id+"'>\n</div>");
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
