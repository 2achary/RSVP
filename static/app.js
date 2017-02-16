var app = angular.module('Rsvp',['ngRoute', 'ngResource']);

app.config(['$routeProvider', '$httpProvider', function ($routeProvider, $httpProvider) {
    $routeProvider
        .when('/guest_list', {
            templateUrl: 'static/guest_list.html',
            controller: 'GuestListCtrl'
        })
        .when('/', {
            templateUrl: 'static/rsvp_form.html',
            controller: 'RsvpCtrl'
        })
        .otherwise({redirectTo: '/'});
}]);

app.controller('RsvpCtrl', function ($scope, Guest, RSVP, $timeout) {

    $scope.alertMsg = "";
    // $scope.guest is the model for the first and last name form
    $scope.guest = {};
    $scope.rsvpSearchResults = [];

    $scope.searchGuest = function(){
        $scope.rsvpSearchResults = Guest.query($scope.guest, function(){

        }, function(result){
            $scope.success = false;
            $scope.alertMsg = "No RSVP found for name entered";
            $timeout(function(){$scope.alertMsg = "";}, 3000)
        });
    };

    $scope.getStatus = function(guest){
        if (guest.RSVP){
            return 'Coming';
        } else {
            if (guest.RSVP === false) {
                return 'Not Coming';
            } else {
                return 'Not Submitted';
            }
        }
    };

    $scope.saveRSVP = function(guest){
        var newRSVP = new RSVP(guest);
        newRSVP.$save($scope.guest, function(success){
            $scope.success = true;
            $scope.alertMsg = "RSVP submitted successfully!";
            $timeout(function(){$scope.alertMsg = "";}, 3000);
            $scope.searchGuest();
        },
        function(error){
            $scope.success = false;
            $scope.alertMsg = "Something went wrong. Please try again.";
            $timeout(function(){$scope.alertMsg = "";}, 3000)

        });
    };
    
});


app.controller('GuestListCtrl', function ($scope, RSVP, Guest) {
    $scope.guestModel = {};
    $scope.guests = [];

    $scope.clearForm = function(){
        $scope.guestModel = {};
    }

    $scope.updateGuestQuery = function() {
        $scope.guests = Guest.query(function(guests){
            $scope.total_rsvp = 0;
            guests.forEach(function(guest){
                if (guest.RSVP) {
                    $scope.total_rsvp += 1;
                }
            })
        });
    };

    $scope.updateGuestQuery();

    $scope.addGuest = function () {
;        Guest.save($scope.guestModel);
        $scope.updateGuestQuery();
    };

    $scope.getStatus = function(guest){
        if (guest.RSVP){
            return 'Coming';
        } else {
            if (guest.RSVP === false) {
                return 'Not Coming';
            } else {
                return 'Not Submitted';
            }
        }
    };

    $scope.deleteGuest = function (guest) {
        Guest.delete(guest);
        $scope.updateGuestQuery();
    };
});

app.constant('APIURL', 'http://127.0.0.1:5000');

app.factory('RSVP', function($resource, APIURL) {
    return $resource('/rsvp', {firstname: '@firstName', lastName: '@lastName', answer: '@answer'});
});

app.factory('Guest', function($resource, APIURL) {
    return $resource('/guest', {firstName: '@firstName', lastName: '@lastName'});
});
