// adding event listener for image load
$('#loadImage').click(function () {
    if($('#loadImage').attr('class') === 'plus circle icon'){
        $('#imageInput').click();
    } else {
        pipeLineBuilder();
    }
});

var pipeLineBuilder = function () {
    var toSend = cvDiagram.model.toJSON();
    toSend = $.parseJSON(toSend);
    toSend['dir_id'] = dir['dir_id'];
    $('.loading-icon').css('visibility', 'visible');
    $.ajax({
        url: '/cached/',
        type: 'POST',
        contentType: 'text',
        data: dir,
        dataType: 'json',
        success: function(result) {
            for (var i=0; i<toSend['nodeDataArray'].length; i++) {
                if ($.inArray(toSend['nodeDataArray'][i]['key'], result) != -1) {
                    toSend['nodeDataArray'][i]['src'] = '';
                }
            }
            toSend = JSON.stringify(toSend);
            runner();
        }
    });

    var runner = function () {
        $.ajax({
            url: '/runner/',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: toSend,
            dataType: 'json',
            success: function(result) {
                for (var i=0; i<result.length; i++){
                    var old = cvDiagram.model.nodeDataArray[i];
                    if (old['calculated'] === 'no') {
                        old['src'] = result[i]['src'];
                        old['calculated'] = result[i]['calculated'];
                        cvDiagram.model.updateTargetBindings(old);
                    }
                }
                $('.loading-icon').css('visibility', 'hidden');
            }
        });
    }
};

// event listener for menu switch
$('#join').click(function () {
    $('#function').removeClass('active');
    $('#join').addClass('active');
    $('#menu-header-icon').removeClass('play')
        .addClass('plus');
    $('#menu-header').text("Join with a node");
    $('.function-dropdown').css('display', 'none');
    $('.join-menu').css('display', 'block');
});

$('#function').click(function () {
    $('#join').removeClass('active');
    $('#function').addClass('active');
    $('#menu-header-icon').removeClass('plus')
        .addClass('play');
    $('#menu-header').text("Apply a function");
    $('.join-menu').css('display', 'none');
    $('.function-dropdown').css('display', 'block');
});


// upload and display the original image
var uploadAndDisplay = function (input) {

    var file = input.files[0];

    if (input.files && file) {
        var reader = new FileReader();
        if(file.type === 'image/jpeg' || file.type === 'image/jpg'){

            reader.onload = function (e) {

                var id = Date.now()
                    .toString()
                    .slice(-5, -1);

                $('#originShow')
                    .attr('src', e.target.result)
                    .height(250);

                $('#id-display').html('<b>ID: ' + id + '</b>');

                $("#side-panel").css('visibility', 'visible');
                $("#imageHolder").css('visibility', 'visible');

                model.nodeDataArray = [
                    {
                        key: id,
                        name: 'id\n' + id,
                        src: e.target.result,
                        calculated: 'yes'
                    }
                ];

                cvDiagram.model = model;

            };
            reader.readAsDataURL(input.files[0]);
            $("#loadImage").attr('class', 'chevron circle right icon');

        } else {
            alert('Only jpg files are supported in this demo!');
        }
    }
};

// event listener for go-forward button on modal
$('#go-forward').click(function (event) {

    if ($('#function').hasClass('active')) {
        var fromID = $('#modal-heading')
            .text()
            .split(':')
            .pop().trim();
        var toId = Date.now()
            .toString()
            .slice(-5, -1)
            .trim();
        var func = $('.functionmenu option:selected')
            .val()
            .trim();

        if (func !== 'Filter') {
            cvDiagram.startTransaction("add node and link");
            var newNode = {
                key: toId,
                name: 'id\n' + toId,
                src: '',
                calculated: 'no'
            };
            var newLink = {
                from: fromID,
                to: toId,
                function: func
            };


            cvDiagram.model.addNodeData(newNode);
            cvDiagram.model.addLinkData(newLink);

            cvDiagram.commitTransaction("add node and link");
        }
    } else if ($('#join').hasClass('active')) {
        var withID = $('#id-to-join').val();
        var currID = $('#modal-heading')
            .text()
            .split(':')
            .pop().trim();
        var newID = Date.now()
            .toString()
            .slice(-5, -1)
            .trim();
        var func = $('.jointypemenu option:selected')
            .val()
            .trim();

        var allID = [];
        for (var i=0; i<model.nodeDataArray.length; i++) {
            allID.push(model.nodeDataArray[i]['key']);
        }

        if ($.inArray(withID, allID) !== -1) {
            if (func != 'Join Type') {

                cvDiagram.startTransaction("add node and link");
                var newNode = {
                    key: newID,
                    name: 'id\n' + newID,
                    src: '',
                    calculated: 'no'
                };
                var newLink1 = {
                    from: withID,
                    to: newID,
                    function: func
                };
                var newLink2 = {
                    from: currID,
                    to: newID,
                    function: func
                };

                cvDiagram.model.addNodeData(newNode);
                cvDiagram.model.addLinkData(newLink1);
                cvDiagram.model.addLinkData(newLink2);

                cvDiagram.commitTransaction("add node and link");
            }
        } else {
            alert('invalid ID!');
        }
    }
});