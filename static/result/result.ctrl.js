resultApp.controller("resultCtrl", ["$scope", "ICEService", "ResultService", function($scope, ICEService, ResultService) {
	var self = this;
	
	self.pagination = {
		current: 1
	};
	
	var selected = {}

	self.connected = function() {
		return ICEService.connected
	}
	
	self.results = function() {
		return ResultService.results;
	};
	
	self.result = function() {
		if(self.results()) {
			return self.results()[self.pagination.current - 1];
		}
		else {
			return null;
		}
	}

	self.saveResults = function() {
		return ResultService.saveResults();
	};
	
	self.selected = function() {
		return selected;
	};
	
	self.setSelected = function(ft) {
		selected = ft;
	}
}]);