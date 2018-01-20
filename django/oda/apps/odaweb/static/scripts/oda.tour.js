function doTour(odbFile) {
    var master = odbFile.oda_master;
    if (master.binary.liveMode) {
        // Instance the tour
        var tour = new Tour({
            name: 'live-mode-tour-v1',
            steps: [
                {
                    element: "#platform-btn",
                    title: "Step 1: Select the Platform",
                    content: "Select the machine architecture to target and relevant machine options."
                },
                {
                    element: "#hex",
                    title: "Step 2: Enter Bytes",
                    content: "Enter some bytes to disassemble in Live View."
                },
                {
                    element: "#oda-tabs li:first",
                    title: "Step 3: View Disassembly Listing",
                    content: "The bytes will be disassembled into readable instructions for the target architecture."
                },
                {
                    element: "#menu-item-file",
                    title: "Step 4: Upload a File",
                    content: "You can also upload a file to disassemble, including raw binaries and many common object formats (ELF, PE, COFF, Mach-O, etc.)."
                }],
            storage: window.localStorage
        });

        // Initialize the tour
        tour.init();

        // Start the tour
        tour.start();
    } else {
        // Instance the tour
        var tour = new Tour({
            name: 'file-mode-tour-v1',
            steps: [
                {
                    element: "#addr-bar-canvas",
                    placement: "bottom",
                    title: "Address Bar Navigation",
                    content: "The address bar lets you easily navigate around large files."
                },
                {
                    element: "#editor",
                    placement: "top",
                    title: "Interactive Disassembly",
                    content: "Right-click on the disassembly listing to convert bytes to instructions or vice verse."
                },
                {
                    element: "#sidebar-label-symbols",
                    placement: "bottom",
                    title: "Symbols, Strings, Structs, and Search",
                    content: "Use the sidebar tabs to view a listing of symbols, strings, user-defined structures.  You can also search for strings or binary sequences."
                }
            ],
            storage: window.localStorage
        });

        // Initialize the tour
        tour.init();

        // Start the tour
        tour.start();
    }
}

odaApplication.run(function (odbFile) {
    /* need to wait until angular finishes rendering...here's a kludge */
    setTimeout(function(){ doTour(odbFile) }, 1000);
});