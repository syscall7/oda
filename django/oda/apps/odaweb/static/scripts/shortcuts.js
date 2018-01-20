odaApplication.run(function($rootScope, Docker, odbFile, editor){

    //http://dmauro.github.io/Keypress/
    var listener = new window.keypress.Listener($('body')[0]);

    $(document)
        .on( "focus", 'input[type=text]', function() { listener.stop_listening(); })
        .on( "blur", 'input[type=text]', function() { listener.listen(); });
    $(document)
        .on( "focus", 'textarea', function() { listener.stop_listening(); })
        .on( "blur", 'textarea', function() { listener.listen(); });


    listener.simple_combo("ctrl g", function() {
        console.log("You pressed ctrl g");
        //todo activate textbox
        $rootScope.$broadcast('command.goto');
    });

    listener.simple_combo(';', function(){
         $rootScope.$broadcast('command.comment');
    });

    listener.register_combo({
        keys: 'c',
        is_solitary: true,
        on_keyup: function (e) {
            var activeRowData = editor.getActiveRowData();

            $rootScope.$broadcast('command.dataToCode', activeRowData);
        }
    });

    listener.simple_combo('d', function(){
        var activeRowData = editor.getActiveRowData();
        if (activeRowData != null) {
            $rootScope.$broadcast('command.codeToData', activeRowData);
        }
    });

    listener.simple_combo("ctrl u", function(){
        $rootScope.$broadcast('command.open');
    });

    /*listener.simple_combo("u", function(){
        var activeRowData = editor.getActiveRowData();
        $rootScope.$broadcast('command.undefine',activeRowData );
    });*/

    listener.simple_combo("t", function(){
        $rootScope.$broadcast('command.makeStructType');
    });

    listener.simple_combo("v", function(){
        var activeRowData = editor.getActiveRowData();
        if (activeRowData != null) {
            $rootScope.$broadcast('command.makeStructVariable', activeRowData);
        }
    });

    listener.simple_combo("ctrl f", function(){
        $rootScope.$apply(function(){Docker.select(Docker.docks[2]);});
    });
});