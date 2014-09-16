function Cell(el, section) {
    this.el = el

    this.cellColors = new CellColors()

    this.dropHandler = function(event, ui){
	this.addSection(ui.draggable.data("section"))
    }

    this.init = function(new_section){
	this.el.draggable({
	    stack: ".matrix-cell",
	    helper: "clone",
	})
	this.el.droppable({
	    drop:  this.dropHandler.bind(this)
	})
	if (new_section != null){
	    this.addSection(new_section)
	}
	else{
	    this.removeSection()
	}
	this.el.addClass("matrix-cell")
    }

    this.removeSection = function(){
	this.section = null
	this.el.removeData("section")
	this.el[0].innerHTML = ""
	this.el.addClass("available-cell")
	this.el.droppable("enable")
	this.el.draggable("disable")
	this.el.removeClass("occupied-cell")
    }

    this.addSection = function(section){
	this.section = section
	this.el.data("section", section)
	this.el.addClass("occupied-cell")
	this.el.removeClass("available-cell")
	this.el.css("background-color", this.cellColors.color(section))
	//TODO:  jquery, how am I actually supposed to do this?
	this.el[0].innerHTML = section.emailcode
	this.el.droppable("disable")
	this.el.draggable("enable")
    }

    this.hasSection = function(){
	return this.section != null
    }

    this.init(section)
}

//TODO:  test that cells have appropriate classes
