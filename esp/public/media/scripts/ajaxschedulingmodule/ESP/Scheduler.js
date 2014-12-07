function Scheduler(
    data,
    directoryEl,
    matrixEl,
    garbageEl,
    last_applied_index,
    update_interval
) {
    this.directory = new Directory(data.sections, directoryEl, data.schedule_assignments);
    this.matrix = new Matrix(
	data.timeslots,
	data.rooms,
	data.schedule_assignments,
	data.sections,
	matrixEl,
	garbageEl,
	new ApiClient()
    );

    this.changelogFetcher = new ChangelogFetcher(
	this.matrix,
	new ApiClient(),
	last_applied_index
    );

    this.render = function(){
	this.directory.render();
	this.matrix.render();
	this.changelogFetcher.pollForChanges(update_interval);
    };
};
