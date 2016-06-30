
// Establish a namespace
var monitor = monitor || {};
/*
 * Create a model object within the monitor namespace.
 */
monitor.model = function () {
	"use strict";
	//private vars
	var vnfs;
	var hosts;
  var chains;
	
	function getHost() {
		//return host data get from ajax
		if (typeof hosts === 'undefined') {
			return [];
		} else {
			return hosts;
		}
	}
	
	function getVnf() {
		//return vnf data get from ajax
		if (typeof vnfs === 'undefined') {
			return [];
		} else {
			return vnfs;
		}
	}
	
  function getChains() {
    //return chain data from ajax call
    if (typeof chains === 'undefined') {
      return [];
    } else {
      return chains;
    }
  }

	function getData(type) {
		//ajax call get different kind of data
		$.ajax({
			contentType: "application/json",
			dataType: "json",
			url: "http://localhost:5000/get"+type,
			method: 'GET',
			success: function (json) {
        if (type == "Chain") {
				  console.log(json);
        }
				if(type === "Host") hosts = json;
				else if (type === "VNF") vnfs = json;
        else if (type === "Chain") chains = json;
			},
			error: function (request, status, error) {
				alert("Web Service is Unavailable: " +
					request.responseText + "\nCheck the Console for details!");
		}
		});
	}
	
	function makeReq(host,ID,action,image,username,vnfname) {
		//send command from frontend to server
		var data;
		if (action == 'create') {
			data = JSON.stringify({'Host' : host,
											'vnfname' : vnfname,
											'image' : image,
											'username' : username,
											'action' : 'deploy'});
		} else {
			data = JSON.stringify({'Host' : host,
											'ID' : ID,
											'action' : action});
		}
		$.ajax({
			contentType: "application/json",
			dataType: "json",
			url: "http://localhost:5000/request",
			data: data,
			method: 'POST',
			success: function (json) {
				console.log(json);
			},
			error: function (request, status, error) {
				alert("Web Service is Unavailable: " +
						request.responseText + "\nCheck the Console for details!");
			}	
		});
	}
	
	function test() {
		alert("Test!");
	}
	
	return {
		//public functions
		test : test,
		getData : getData,
		getHost : getHost,
		getVnf : getVnf,
		makeReq : makeReq
	};
};
