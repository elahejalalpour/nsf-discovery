
// Establish a namespace
var monitor = monitor || {};

/*
 * Create a model object within the electionViz namespace.
 */
monitor.model = function () {
	"use strict";
	//private vars
	var vnfs;
	var hosts;
	
	function getHost() {
		return hosts;
	}
	
	function getVnf() {
		return vnfs;
	}
	
	function getData(type) {
	/*
		var data = JSON.stringify({
					"candidates": candidatePositions,
					"size": size,
					"numVoters": numVoters,
					"sigma": sigma
		});
		console.log(data);
	*/
		$.ajax({
			contentType: "application/json",
			dataType: "json",
			url: "http://localhost:5000/get"+type,
			method: 'GET',
			success: function (json) {
				//console.log(json);
				if(type === "Host") hosts = json;
				else vnfs = json;
			},
			error: function (request, status, error) {
				alert("Web Service is Unavailable: " +
					request.responseText + "\nCheck the Console for details!");
		}
		});
	}
	
	function makeReq(host,ID,action) {
		var data = JSON.stringify({'Host' : host,
											'ID' : ID,
											'action' : action});
		
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
		test : test,
		getData : getData,
		getHost : getHost,
		getVnf : getVnf,
		makeReq : makeReq
	};
};
