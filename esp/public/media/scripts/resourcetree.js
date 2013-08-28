function createAbstractResource (node) {
    $j(".jstree").jstree("create_node",node,"inside",{
        "data" : {
            "title" : "New Abstract Resource",
            "attr" : {
                "id" : "abstract-resource-add",
                "rel" : "abstract-resource",
            }
        },
    });
    $j("#id_resource_type","#form-abstract-resource-add").attr("value",node.context.id.replace("new-resource-type-",""));
}

function createNewResourceType (node) {
    $j(".jstree").jstree("create_node",node,"inside",{
        "data" : {
            "title" : "New Resource Type", // which, of course, is really a New NewResourceType...
            "attr" : {
                "id" : "new-resource-type-add",
                "rel" : "new-resource-type",
            }
        },
    });
    if (node) {
        $j("#id_parent","#form-new-resource-type-add").attr("value",node.context.id.replace("new-resource-type-",""));
    }
}

function renderTree(container) {
    var tree = container.jstree({
        "plugins" : ["themes", "html_data", "ui", "dnd", "crrm", "contextmenu"],
        "ui" : {
            "select_limit" : 1,
        },
        "crrm" : {
            "move" : {
                "check_move" : function (move) {
                    if (move.cr==-1) {
                        //if we're moving to root, we must be a NRT
                        return (move.o.context.id.indexOf("abstract-resource")==-1);
                    } else {
                        //otherwise we can be an AR but must still move under an NRT
                        return (move.cr.context.id.indexOf("abstract-resource")==-1);
                    };
                },
            },
        },
        "contextmenu" : {
            "items" : function (node) {
                var menu = {};
                menu.del = {
                    "label" : "Delete",
                    "action" : function (obj) {
                        if (confirm("Are you sure you want to delete "+$j(".jstree").jstree("get_text",node)+" and all its children?")) {
                            var form = $j("#form-"+node.context.id);
                            $j("#id_is_active",form).attr("value","False");
                            console.log(form);
                            form.submit();
                            $j(".jstree").jstree("delete_node", node);
                        }
                    }
                };
                if (node.context.id.indexOf("abstract-resource")==-1) {
                    menu.createNewResourceType = {
                        "label" : "Create Resource Type",
                        "action" : createNewResourceType,
                    };
                    menu.createAbstractResource = {
                        "label" : "Create Abstract Resource",
                        "action" : createAbstractResource,
                    };
                }
                return menu;
            },
        },
    });
    tree.bind("select_node.jstree", function (event, data) {
        $j(".abstract-resource").css("display","none");
        $j(".new-resource-type").css("display","none");
        $j("#view-" + data.args[0].id).css("display","");
    });
    tree.bind("move_node.jstree", function (event, data) {
        var move = data.args[0];
        var childForm = $j("#form-" + move.o.context.id);
        if (move.cr==-1) {
            var parentId = "";
        } else {
            var parentId = move.cr.context.id.replace("new-resource-type-","");
        }
        if (move.o.context.id.indexOf("abstract-resource")==-1) {
            //if we're moving a NRT
            $j("#id_parent", childForm).attr("value",parentId);
        } else {
            //if we're moving an AR
            $j("#id_resource_type", childForm).attr("value",parentId);
        }
        childForm.submit();
    });
}

function submitMe () {
    var button = $j(".button",this);
    button.attr("value","Saving...");
    var thisId = $j(this).attr("id");
    var name = $j("#id_name",this).attr("value");
    $j.post($j(this).attr("action"), $j(this).serialize(), function(response) {
        //will do something soon
        if (response) {
            alert(response);
        } else {
            button.attr("value","Saved");
            $j(".jstree").jstree("rename_node",thisId.replace("form-","#"),name);
        }
    });
    return false;
};
