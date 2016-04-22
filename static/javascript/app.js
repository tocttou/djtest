var dir = {dir_id: Math.floor(Date.now()/1000)};

// Show instructions modal
$('#instructions-modal')
    .modal('show');
$('#got-it').click(function () {
    $('#instructions-modal')
        .modal('hide');
});

// Creating the diagram object
var GO = go.GraphObject.make;
var cvDiagram =
    GO(go.Diagram, "cvDiagramDiv",
        {
            initialContentAlignment: go.Spot.Center,
            "undoManager.isEnabled": true,
            "allowCopy": false,
            layout: GO(go.LayeredDigraphLayout)
        });

// link template for the diagram object
cvDiagram.linkTemplate =
    GO(go.Link,
        { routing: go.Link.Orthogonal, corner: 5 },
        GO(go.Shape, { strokeWidth: 3, stroke: "#555" }),
        GO(go.Panel, "Auto",
            GO(go.Shape, "rectangle", { fill: "yellow", stroke: "gray" }),
            GO(go.TextBlock, { margin: 3 },
                new go.Binding("text", "function"))
        ),
        GO(go.Shape, { toArrow: "Standard" })
    );

// node template for the diagram object
cvDiagram.nodeTemplate =
    GO(go.Node, "Horizontal",
        { background: "#44CCFF" },
        GO(go.Picture, { maxSize: new go.Size(100, 100) },
            new go.Binding("source", "src")),
        {
            selectionAdornmentTemplate:
                GO(go.Adornment, "Auto",
                    GO(go.Shape, "RoundedRectangle",
                        { fill: null, stroke: "dodgerblue", strokeWidth: 8 }),
                    GO(go.Placeholder)
                )
        },
        GO(go.TextBlock, "Default Text",
            { margin: 12, stroke: "white", font: "bold 16px sans-serif" },
            new go.Binding("text", "name"))
    );

var model = GO(go.GraphLinksModel);


// adding eventlisteners to the diagram object
cvDiagram.addDiagramListener("ObjectDoubleClicked", function (ev) {
    var part = ev.subject.part;
    if (!(part instanceof go.Link)){
        $('#modal-heading').text('Select an action for node: ' + part.data.key);
        $('#function-modal').modal('show');
        $('.ui.dropdown').dropdown();
    }
});

cvDiagram.addDiagramListener("ObjectSingleClicked", function (ev) {
    var part = ev.subject.part;
    if (!(part instanceof go.Link)){
        if (part.data.src !== '') {
            $('#originShow')
                .attr('src', part.data.src)
                .height(250).show();
        } else {
            $('#originShow').hide();
        }
        $('#id-display').html('<b>ID: ' + part.data.key + '</b>');
    }
});


cvDiagram.addDiagramListener("SelectionDeleted", function(ev) {
    var numNodes = $.parseJSON(
        cvDiagram.model.toJSON()
    )['nodeDataArray'].length;
    if (numNodes === 0) {
        $("#imageHolder").css('visibility', 'hidden');
        $("#loadImage").attr('class', 'plus circle icon');
    }
});