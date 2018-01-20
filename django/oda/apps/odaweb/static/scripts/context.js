"use strict";

odaApplication.run(function($rootScope, editor, odbFile){
    //http://lab.jakiestfu.com/contextjs/
    context.init({preventDoubleContext: false});

    context.show.add(function(menu, e){
        editor.setActiveCellFromEvent(e);
        var rowData = editor.getActiveRowData();



        if (rowData == null) {
            return;
        }

        var isCode = rowData.isCode;

        console.log("context-show", rowData);

        var shortcuts = menu.find('.shortcut-text');
        shortcuts.removeClass('shortcut-text-disabled');

        if (isCode) {
            $('.data-only').addClass('shortcut-text-disabled');
        } else {
            $('.code-only').addClass('shortcut-text-disabled');
        }

        /*
        var session = editor.getSession();

        var cursor = session.getSelection().getCursor();
        var line = session.getDocument().getLineData(cursor.row);

        var section = odbFile.getSection(line.data.section_name);
        */

        /*if (section.isData()) {
            shortcuts.addClass('shortcut-text-disabled');
        }*/
    });

    var createAction = function(f) {

        return function(e) {

            if ($(e.target).hasClass('shortcut-text-disabled')) {
                //diasbled?
                return;
            }

            var activeRowData = editor.getActiveRowData();

            /*var session = editor.getSession();

            var cursor = session.getSelection().getCursor();
            var line = session.getDocument().getLineData(cursor.row);*/

            f(activeRowData);
        };
    };

    context.attach('#editor', [

		{header: 'ODA Commands'},
		/*{text: 'The Author', subMenu: [
			{header: '@jakiestfu'},
			{text: 'Website', href: 'http://jakiestfu.com/', target: '_blank'},
			{text: 'Forrst', href: 'http://forrst.com/people/jakiestfu', target: '_blank'},
			{text: 'Twitter', href: 'http://twitter.com/jakiestfu', target: '_blank'},
			{text: 'Donate?', action: function(e){
				e.preventDefault();
				$('#donate').submit();
			}}
		]},*/
        {
            text: '<span class="shortcut-text">Comment</span><span class="shortcut-key">;</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.comment', data); })
        },
        {
            text: '<span class="shortcut-text code-only">Code -> Data</span><span class="shortcut-key">d</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.codeToData', data); })
        },
        {
            text: '<span class="shortcut-text data-only">Data -> Code</span><span class="shortcut-key">c</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.dataToCode', data); })
        },
        {
            text: '<span class="shortcut-text code-only">Create/Edit Function</span><span class="shortcut-key">t</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.makeFunction', data); })
        },
        {
            text: '<span class="shortcut-text data-only">Create/Edit Variable</span><span class="shortcut-key">v</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.makeStructVariable', data); })
        }
        /*,
        {
            text: '<span class="shortcut-text">Undefine</span><span class="shortcut-key">u</span>',
            action: createAction(function (data) { $rootScope.$broadcast('command.undefine', data ); })
        }*/

        /*,
        {divider: true}


		{text: 'Hmm?', subMenu: [
			{header: 'Well, thats lovely.'},
			{text: '2nd Level', subMenu: [
				{header: 'You like?'},
				{text: '3rd Level!?', subMenu: [
					{header: 'Of course you do'},
					{text: 'MENUCEPTION', subMenu: [
						{header:'FUCK'},
						{text: 'MAKE IT STOP!', subMenu: [
							{header: 'NEVAH!'},
							{text: 'Shieeet', subMenu: [
								{header: 'WIN'},
								{text: 'Dont Click Me', href: 'http://bit.ly/1dH1Zh1', target:'_blank', action: function(){
									_gaq.push(['_trackEvent', 'ContextJS Weezy Click', this.pathname, this.innerHTML]);
								}}
							]}
						]}
					]}
				]}
			]}
		]}*/
	]);

});
