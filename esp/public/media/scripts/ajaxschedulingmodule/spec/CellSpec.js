describe("Cell", function(){
    beforeEach(function(){
	c = new Cell($j("<td/>"), null, "1-115", 1)

	section = {
	    emailcode: "my-emailcode",
	}
    })

    it("has an element with the matrix cell class", function(){
	expect(c.el).toBeDefined()
	expect(c.el.hasClass("matrix-cell")).toBeTrue()
    })

    it("has a room attached as data on the el", function(){
	expect(c.room_name).toEqual("1-115")
    })

    it("has a timeslot", function(){
	expect(c.timeslot_id).toEqual(1)
    })

    it("attaches itself to its el", function(){
	expect($j(c.el).data("cell")).toEqual(c)
    })

    describe("init", function(){
	it("makes the element draggable", function(){
	    spyOn(c.el, 'draggable')
	    c.init(section)
	    expect(c.el.draggable).toHaveBeenCalled()
	})

	it("makes the element droppable", function(){
	    spyOn(c.el, 'droppable')
	    c.init(section)
	    expect(c.el.droppable).toHaveBeenCalled()
	})

	describe("with a section", function(){
	    it("has a section", function(){
		spyOn(c, 'addSection')
		c.init(section)
		expect(c.addSection).toHaveBeenCalledWith(section)
	    })
	})

	describe("without a section", function(){
	    it("calls removeSection", function(){
		spyOn(c, 'removeSection')
		c.init(null)
		expect(c.removeSection).toHaveBeenCalled()
	    })
	})
    })

    describe("adding a section", function(){
	beforeEach(function(){
	    c.removeSection()
	})
	it("saves off the section", function(){
	    c.addSection(section)
	    expect(c.section).toEqual(section)
	})
	it("adds the section to the element", function(){
	    c.addSection(section)
	    expect(c.el[0].innerHTML).toEqual(section.emailcode)
	})
	it("adds styling to the el", function(){
	    c.addSection(section)
	    expect(c.el.hasClass("occupied-cell")).toBeTrue()
	    expect(c.el.hasClass("available-cell")).toBeFalse()
	})
	it("adds the section to the el data", function(){
	    c.addSection(section)
	    expect(c.el.data("section")).toEqual(section)
	})
	it("makes the el draggable", function(){
	    c.addSection(section)
	    expect(c.el.draggable("option", "disabled")).toBeFalse()
	})
	it("makes the el not droppable", function(){
	    c.addSection(section)
	    expect(c.el.droppable("option", "disabled")).toBeTrue()
	})
    })

    describe("removing a section", function(){
	beforeEach(function(){
	    c.addSection(section)
	})
	it("removes the section", function(){
	    c.removeSection()
	    expect(c.section).toBeNull()
	})
	it("changes the el contents", function(){
	    c.removeSection()
	    expect(c.el[0].innerHTML).not.toMatch(section.emailcode)
	})
	it("removes the section from the el data", function(){
	    c.removeSection()
	    expect(c.el.data("section")).not.toBeDefined()
	})
	it("changes the cell styling", function(){
	    c.removeSection()
	    expect(c.el.hasClass("occupied-cell")).toBeFalse()
	    expect(c.el.hasClass("available-cell")).toBeTrue()
	})
	it("makes the cell droppable", function(){
	    c.removeSection()
	    expect(c.el.droppable("option", "disabled")).toBeFalse()
	})
	it("makes the cell not draggable", function(){
	    c.removeSection()
	    expect(c.el.draggable("option", "disabled")).toBeTrue()
	})
    })

    describe("hasSection", function(){
	it("returns true when the cell has a section", function(){
	    c.addSection({ emailcode: "S1234s1"})
	    expect(c.hasSection()).toBeTrue()
	})

	it("returns false when there is no section", function(){
	    expect(c.hasSection()).toBeFalse()
	})
    })
})
