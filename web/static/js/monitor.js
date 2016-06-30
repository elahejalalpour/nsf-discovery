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
	
  function drawChain(chain) {
    var nodes = [];
    var links = [];
    var LENGTH_MAIN = 350,
        LENGTH_SERVER = 150,
        LENGTH_SUB = 50,
        WIDTH_SCALE = 2,
        GREEN = 'green',
        RED = '#C5000B',
        ORANGE = 'orange';
    console.log(chain)
    for (var i = 0; i < chain['nodes'].length; ++i) {
      nodes.push({id: i, group: 'container'});  
    }

    for (var i = 0; i < chain['links'].length; ++i) {
      var s = chain['links'][i]['source'];
      var t = chain['links'][i]['target'];
      links.push({from: s, to: t, length: LENGTH_MAIN, width: WIDTH_SCALE * 6, label: '0.71 mbps'})
    }
    var chain_canvas = document.getElementById('Chain');
    var render_data = {
      nodes: nodes,
      edges: links
    };
    var options = {
      nodes: {
        scaling: {min: 12, max: 16}
      },
      edges: {
        color: RED,
        smooth: true
      },
      groups: {
        'container': {
          shape: 'triangle',
          color: GREEN
        }
      }
    };
    var chain_drawing = new vis.Network(chain_canvas, render_data, options);
  }

	function repeat() {
		//repeat every 2 seconds
		setTimeout(repeat, 5000);
		$("#Hosts").empty();
		$("#VNFS").empty();
		$("#Chain").empty();
		
		var changed = false;
		
		model.getData("VNF");
		var vnfs = model.getVnf();
		model.getData("Host");
		var hosts = model.getHost();
    model.getData("Chain");
    var chains = model.getChains();
		console.log(JSON.stringify(chains));
		var data = JSON.stringify(vnfs);
		//console.log("d:"+$('#fresh').text());
		var old = $('#fresh').text();
		
		if (data !== old) {
			$('#fresh').text(data);
			changed = true;
			$('#popup').empty()
			console.log("VNF data changed");
		}
    // Chains Tab
    for (var i = 0; i < chains.length; ++i) {
      drawChain(chains[i]);
    }
		//VNF Tab
		for(var i = 0; i < hosts.length; i++) {
			//console.log(hosts[i]);
			var hostname = hosts[i]['Host_name'];
			var IP = hosts[i]['Host_ip'];
			var cpu = hosts[i]['Host_cpu'];
			var ram = Math.round(hosts[i]['Host_used_mem']/hosts[i]['Host_total_mem']*100);
			var active = hosts[i]['Active'];
			var images = hosts[i]['images'];
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
					result+="<a id="+hostname+"_button class='mybutton'>Hide VNFS</a>";
				} else {
					result+="<a id="+hostname+"_button class='mybutton'>Show VNFS</a>";
				}
				//add start button
				result+="<a id="+hostname+"_start class='mybutton'>Start All</a>";
				//add stop button
				result+="<a id="+hostname+"_stop class='mybutton'>Stop All</a>";
				//add deploy button
				result+="<a class='mybutton' href=#"+hostname+"_deploy>Deploy</a>";
				
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
					model.makeReq(args[0],'*',args[1],'','','');
				});
				//add stop all listener
				$("#"+hostname+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],'*',args[1],'','','');
				});
				//add deploy dialog box
				if (changed) {
					result="<div id="+hostname+"_deploy class='modalDialog'>"
											+`<div>
												<a href="#close" title="Close" class="close">X</a>
												<h2>VNF Deployment</h2>`;
					result+="<h3 style='margin: 0 0 0.8em 0'>Host: "+hostname+"</h3>";
					result+="<label style='font-size:14pt'>Image: </label>"
								+"<select style='margin: 0 0 0.4em 0' id='"+hostname+"_image'>";
					for (var k = 0; k < images.length; k++) {
						result+="<option>"+images[k]+"</option>"
					}
					result+="</select></label><br>"
					
					result+="VNF Name: <input style='margin: 0 0 0.4em 0'" 
								+"type='text' class ='glowing-border' id='"+
								hostname+"_vnfname'></input><br>";
					result+="User Name: <input style='margin: 0 0 0.4em 0'"
								+"type='text' class ='glowing-border' id='"+
								hostname+"_username'></input><br>";
					result+="<a href='#close' class='mybutton' id='"+hostname
								+"_create'>Deploy It!</a>";
				
					result+="</div></div>";
					$('#popup').append(result);
				
				
					//add deploy listener
					$("#"+hostname+"_create")[0].addEventListener('click', function () {
						var args = this.id.split("_");
						var username = $('#'+args[0]+'_username').val();
						var image = $('#'+args[0]+'_image').val();
						var vnfname = $('#'+args[0]+'_vnfname').val();
						if(username === '' || vnfname === '') {
							alert('Empty Input!');
						} else {
							console.log(this.id+' '+username+' '+image+' '+vnfname);
							model.makeReq(args[0],'',args[1],image,username,vnfname);
							$('#'+args[0]+'_username').val('');
							$('#'+args[0]+'_vnfname').val('');
						}
					});
				}	
				
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
				//cpu
				result+="<p style='margin:0 0 1em'>Status:"
							+"<span style='color:green'> Running</span></p>"
				result+="<p style='width:100%;font-weight:bold' data-value='"
							+cpu+"'>CPU ("+cpus.length+" cores)</p>";
				result+="<progress max='100' value='"+cpu+"' class='css3'>";
				result+=`<div class='progress-bar'>
								<span style='width: 80%'>80%</span>
							</div>
							</progress>`;
				result+="<p style='font-size:8'> Cores:</p>";
				//cores		
				for(var j = 0; j < cpus.length; j++) {
					result+="<span style='font-size:10pt'>["+j+"]:</span>";
					result+="<progress max='100' value='"+cpus[j]+"' class='css3' id='CPU'>";
					result+=`<div class='progress-bar'>
									<span style='width: 80%'>80%</span>
								</div>
								</progress>`;
					if ((j % 2) === 1) result+="<br>";
				}
				//result+="<br></br>"
				//ram
				var total_ram = Math.round(hosts[i]['Host_total_mem']/1024/1024);
				var used_ram = Math.round(hosts[i]['Host_used_mem']/1024/1024);
				result+="<p style='width:100%;font-weight:bold;margin:1em 0 0 0' data-value='"
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
			//if ((i % 2) === 1) result+="<br></br><br></br><br></br>";
			result+="</li>";
			$('#Hosts').append(result);
		}
		
		//add VNF entries under VNF Tab
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
				//add start button and listener
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_start>Start</button>")
				$("#"+hostname+"_"+id+"_start")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2],'','','');
				});
				//add stop button and listener
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_stop>Stop</button>")
				$("#"+hostname+"_"+id+"_stop")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2],'','','');
				});
				//add destroy button and listener
				$("."+hostname+id).append("<button id="+hostname+"_"+id+"_destroy>Destroy</button>")
				$("#"+hostname+"_"+id+"_destroy")[0].addEventListener('click', function () {
					console.log(this.id);
					var args = this.id.split("_");
					model.makeReq(args[0],args[1],args[2],'','','');
				});
			}
		}
	}
	repeat()
	
});
