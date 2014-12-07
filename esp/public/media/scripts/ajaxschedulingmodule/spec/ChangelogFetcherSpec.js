describe("ChangelogFetcher", function() {
    var c = new ChangelogFetcher(new FakeMatrix(), new FakeApiClient(), 10000000000, 32)

    var changelog_entry = {
	id: 3538,
	index: 2,
	room_name: "room-2",
	timeslots: [ "1", "2" ],
    }

    var unschedule_changelog_entry = {
	timeslots: [],
	room_name: "",
	id: 3329,
	index: 3,
    }

    var changelog = {
	changelog: [changelog_entry, unschedule_changelog_entry]
    }

    it("should set the last_applied_index", function(){
	expect(c.last_applied_index).toEqual(32)
    })

    describe("getChanges", function(){
	it("calls the API client", function(){
	    spyOn(c.api_client, "get_change_log")
	    c.getChanges()

	    expect(c.api_client.get_change_log).toHaveBeenCalled()
	    //TODO: assert on the parameters
	})
    })

    describe("pollForChanges", function(){
	it("sets an interval", function(){
	    spyOn(window, "setInterval");
	    c.pollForChanges(1234567)

	    expect(window.setInterval).toHaveBeenCalled()
	    args = window.setInterval.argsForCall[0]
	    expect(args[1]).toEqual(1234567)
	})
    })

    describe("applyChangeLog", function(){
	it("schedules the classes locally", function(){
	    spyOn(c.matrix, "scheduleSectionLocal")
	    c.applyChangeLog(changelog)
	    expect(c.matrix.scheduleSectionLocal).toHaveBeenCalled()

	    var args = c.matrix.scheduleSectionLocal.argsForCall[0];
	    expect(args[0]).toEqual(section_2().id);
	    expect(args[1]).toEqual("room-2");
	    expect(args[2]).toEqual(["1", "2"]);
	})

	it("unschedules the classes locally", function(){
	    spyOn(c.matrix, "unscheduleSectionLocal")
	    c.applyChangeLog(changelog)
	    expect(c.matrix.unscheduleSectionLocal).toHaveBeenCalled()

	    var args = c.matrix.unscheduleSectionLocal.argsForCall[0]
	    expect(args[0]).toEqual(section_1().id)
	})

	it("updates the last fetched number", function(){
	    c.applyChangeLog(changelog)
	    expect(c.last_applied_index).toEqual(3);
	})
    })
})
