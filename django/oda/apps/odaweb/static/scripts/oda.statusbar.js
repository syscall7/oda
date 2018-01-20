var StatusBar = function(odbFile) {
    this.setAddress = function(address) {
        $('.ace_status-indicator').html("0x" + address.toString(16));
    };

    var projectNameTemplate = Handlebars.compile('{{odaMaster.project_name}} : {{odaMaster.binary.arch}} ({{odaMaster.binary.size}})');
    $('.oda_status-name-box').html(projectNameTemplate({
        odaMaster: odbFile.oda_master
    }));

    this.defaultTemplateString = "[{{mode}}] {{status}}";
    this.updateTemplateString = '[{{mode}}] <span style="background-color:#00842D; color:white;">{{status}}</span>';
    var defaultStatus = 'ONLINE DISASSEMBLER 4EVER!';
    this.status = 'ONLINE DISASSEMBLER 4EVER!';

    var mode = 'normal';

    this._setStatus = function(templateString){
        var template = Handlebars.compile(templateString);
        var renderedText = template({mode:mode, status: this.status});
        $('.status-mode').html(renderedText);
    };
    this._setStatus(this.defaultTemplateString);


    var timer = null;
    this.pushStatus = function(newStatus) {
        this.status = newStatus;
        this._setStatus(this.updateTemplateString);
        if (timer != null) {
            clearInterval(timer);
        }
        timer = setTimeout(function(){
            timer = null;
            this.status = defaultStatus;
            this._setStatus(this.defaultTemplateString);
        }.bind(this), 5000);

    }




    var ajaxOuts = 0;
    $( document ).ajaxSend(function(e, jqXHR, ajaxOptions){
        if (ajaxOuts == 0) {
            $('.oda_loading-indicator').fadeOut(250).fadeIn(250).fadeOut(250).fadeIn(250);
        }
        ajaxOuts +=1;
        //console.log("ajaxSend", e, jqXHR, ajaxOptions);
    } );
    $( document ).ajaxSend(function(e, jqXHR, ajaxOptions){
        ajaxOuts -= 1;
        if (ajaxOuts == 0) {
            $('.oda_loading-indicator').fadeOut(500);
        }
    });

    var errorTemplate = Handlebars.compile("<p>{{time}}: {{thrownError}} -- {{url}}</p>");
    $(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError){
        $('.oda_error-indicator').fadeIn(250);
        console.log(jqXHR, ajaxSettings.url, thrownError);
        var d = new Date();
        $('.oda-error-messages').append(errorTemplate({
            thrownError: thrownError,
            url: ajaxSettings.url,
            time: d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds() + "." + d.getMilliseconds()
        }));
    });

    $('.oda_error-indicator').click(function(){
        $('#messages-container').slideToggle();
    });
};