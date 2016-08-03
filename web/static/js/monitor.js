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
      $('#navi-new-chain').prop('hidden', 'hidden');
      $('#navi-show-chains').prop('hidden', 'hidden');
      $('#new-chain').prop('hidden', 'hidden');
      $('#show-chain').prop('hidden', 'hidden');
      $('#Hosts').removeProp('hidden');
  });
  
  $("#navi-vnfs")[0].addEventListener('click', function () {
      $("a").removeClass('active');
      $("#navi-vnfs").addClass('active');
      $('#Hosts').prop('hidden', 'hidden');
      $('#navi-new-chain').prop('hidden', 'hidden');
      $('#navi-show-chains').prop('hidden', 'hidden');
      $('#new-chain').prop('hidden', 'hidden');
      $('#show-chain').prop('hidden', 'hidden');
      $('#VNFS').removeProp('hidden');
  });
  
  $("#navi-chain")[0].addEventListener('click', function () {
      $("a").removeClass('active');
      $("#navi-chain").addClass('active');
      $('#Hosts').prop('hidden', 'hidden');
      $('#new-chain').prop('hidden', 'hidden');
      $('#show-chain').prop('hidden', 'hidden');
      $('#VNFS').prop('hidden', 'hidden');
      $('#navi-new-chain').removeProp('hidden');
      $('#navi-show-chains').removeProp('hidden');
  });


  $("#navi-show-chains")[0].addEventListener('click', function () {
      $("a").removeClass('active');
      $("#navi-chain").addClass('active');
      $('#Hosts').prop('hidden', 'hidden');
      $('#VNFS').prop('hidden', 'hidden');
      $('#navi-new-chain').removeProp('hidden');
      $('#navi-show-chains').removeProp('hidden');
      $('#new-chain').remove();
      $('#show-chain').remove();
      $('#chains').append("<div id = 'show-chain' style='width:100%;height:750px'></div>")
      $('#show-chain').removeProp('hidden');
      // Chains Tab
      model.getData("Chain");
      var chains = model.getChains();
      console.log(JSON.stringify(chains));
      for (var i = 0; i < chains.length; ++i) {
        $("#show-chain").append("<div id=chain"+i+" style='width: 80%;height: 200px;'></div>")
        drawChain(chains[i], "chain" + i);
      }
  });
  
  $("#navi-new-chain")[0].addEventListener('click', function () {
      $("a").removeClass('active');
      $("#navi-chain").addClass('active');
      $('#Hosts').prop('hidden', 'hidden');
      $('#VNFS').prop('hidden', 'hidden');
      $('#navi-new-chain').removeProp('hidden');
      $('#navi-show-chains').removeProp('hidden');
      $('#show-chain').remove()     
      $('#new-chain').remove();
      $('#chains').append("<div id = 'new-chain' style='width:100%;height:100%'></div>")
      $('#new-chain').removeProp('hidden');
      drawChainUI();
  });

  function drawChainUI() {
    var new_chain_div = document.getElementById("new-chain");
    if (new_chain_div == null) {
      return;
    }
    $("#new-chain").append("<h3>Create New Service Chain</h3>");
    $("#new-chain").append("<form id='config-uploader' method = 'post'>");
    $("#new-chain").append("<label>Select Chain Configuration File (*.json)</label></br>"); 
    $("#new-chain").append("<input type = 'hidden' id = 'action' value = 'create_chain'/>");
    $("#new-chain").append("<input type = 'file' id = 'chain-config'/>");
    $("#new-chain").append("<a id = 'upload-button' class = 'mybutton'>Create Chain</a>");
    $("#new-chain").append("</form>");
    $("#upload-button").click(function() {
      var formData = new FormData($("#config-uploader")[0]);
      console.log($('#chain-config')[0].files[0]);
      formData.append('file', $('#chain-config')[0].files[0]);
      model.createChainRequest(formData);
    });
  }

  function drawChain(chain, canvas_id) {
    var nodes = [];
    var links = [];
    var LENGTH_MAIN = 350,
        LENGTH_SERVER = 150,
        LENGTH_SUB = 50,
        WIDTH_SCALE = 2,
        GREEN = 'green',
        RED = '#C5000B',
        BLACK = '#090909',
        ORANGE = 'orange';
    console.log(chain)
    var chain_canvas = document.getElementById(canvas_id);
    if (chain_canvas == null) return;
    for (var i = 0; i < chain['nodes'].length; ++i) {
      var title_text = "VNF Type: " + chain['nodes'][i]['type'];
      nodes.push({id: i, group: chain['nodes'][i]['type'], value: 25, label: chain['nodes'][i]['name'], title: title_text});  
    }

    for (var i = 0; i < chain['links'].length; ++i) {
      var s = chain['links'][i]['source'];
      var t = chain['links'][i]['target'];
      links.push({from: s, to: t, length: LENGTH_SERVER, color: BLACK, width: WIDTH_SCALE * 2})
    }

    var render_data = {
      nodes: nodes,
      edges: links
    };
    var options = {
      layout:{ randomSeed:105, improvedLayout: true },
      interaction: {hover: true},
      nodes: {
        size: 60,
        scaling: {min: 20, max: 40},
        font: {
          size: 14,
          face: 'Ubuntu',
          align: 'center'
        },
        shadow: true
      },
      edges: {
        color: RED,
        smooth: {enabled: true, type: "dynamic", roundness: 0.5}
      },
      groups: {
        'firewall': {
          shape: 'circularImage',
          image: 'static/images/firewall.jpg' 
        },
        'proxy': {
          shape: 'circularImage',
          image: 'static/images/proxy.png'
        }
      }
    };
    var chain_drawing = new vis.Network(chain_canvas, render_data, options);
  }

  function repeat() {
    //repeat every 2 seconds
    setTimeout(repeat, 1500);
    $("#Hosts").empty();
    $("#VNFS").empty();
    
    var changed = false;
    
    model.getData("VNF");
    var vnfs = model.getVnf();
    model.getData("Host");
    var hosts = model.getHost();
    var data = JSON.stringify(vnfs);
    //console.log("d:"+$('#fresh').text());
    var old = $('#fresh').text();
    
    if (data !== old) {
      $('#fresh').text(data);
      changed = true;
      $('#popup').empty()
      console.log("VNF data changed");
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
        result+=`<p> <span style='font-weight: bold; font-size: 12pt'> 
              Container ID: </span>`+`<span style='font-family: Consolas, monaco, monospace'>` + id.substring(0,11) + `</span>`;
        result+=`, <span style='font-weight: bold; 
              font-size: 12pt'> Type: </span>`+type+"</p>";
        result+=`<p><span style='font-weight: bold; 
              font-size: 12pt'> Name: </span>`+vnfname;
        result+=", <span style='font-weight: bold; font-size: 12pt'> IP: </span>"+IP;
        var status_color = "green";
        if (status != "running") status_color = "red";
        result+=`<br/><span style='font-weight: bold; 
              font-size: 12ppt;'> Status: </span>`+`<span style='color:`+status_color+`'>`+status+`</span></p>`;
        $("."+hostname+id).append(result);
        //add start button and listener
        $("."+hostname+id).append("<a id="+hostname+"_"+id+"_start class='mybutton'>Start</a>")
        $("#"+hostname+"_"+id+"_start")[0].addEventListener('click', function () {
          console.log(this.id);
          var args = this.id.split("_");
          model.makeReq(args[0],args[1],args[2],'','','');
        });
        //add stop button and listener
        $("."+hostname+id).append("<a id="+hostname+"_"+id+"_stop class='mybutton'>Stop</a>")
        $("#"+hostname+"_"+id+"_stop")[0].addEventListener('click', function () {
          console.log(this.id);
          var args = this.id.split("_");
          model.makeReq(args[0],args[1],args[2],'','','');
        });
        //add destroy button and listener
        $("."+hostname+id).append("<a id="+hostname+"_"+id+"_destroy class='mybutton'>Destroy</a>")
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
