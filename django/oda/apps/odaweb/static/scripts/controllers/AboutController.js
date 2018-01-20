odaApplication.controller('AboutController', function AboutController($scope) {

    var rev = '$LastChangedRevision: 1759 $'.split(' ')[1];
    $scope.release_version = '0.3.0' + rev;
    $scope.release_date = '$LastChangedDate: 2015-04-22 02:41:20 +0000 (Wed, 22 Apr 2015) $'.split(' ')[1]
});

