partsGenieApp.factory("PartsGenieService", [function() {
	var obj = {};
	obj.query = {
			"app": "PartsGenie",
			"designs": [
				{
					"dna": {
						"name": "",
						"desc": "",
						"features": [
							{"typ": "http://purl.obolibrary.org/obo/SO_0001416", "seq": "", "name": "5\' flanking region", "temp_params": {"fixed": true}},
							{"typ": "http://purl.obolibrary.org/obo/SO_0000139", "end": 60, "name": "ribosome entry site", "parameters": {"TIR target": 15000}, "temp_params": {"fixed": false}},
							{"typ": "http://purl.obolibrary.org/obo/SO_0000316", "options": [{"typ": "http://purl.obolibrary.org/obo/SO_0000316", "name": "coding sequence", "temp_params": {"aa_seq": "", "fixed": false}}]},
							{"typ": "http://purl.obolibrary.org/obo/SO_0001417", "seq": "", "name": "3\' flanking region", "temp_params": {"fixed": true}}
						]
					}
				}
			], 
			"filters": {
				"max_repeats": 6
			},
		};

	return obj;
}]);