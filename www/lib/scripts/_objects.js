function Registry() {
	this.events = {};
}

Registry.prototype.on = function registerEvent(tag) {
	var args = splatArgs(Registry.prototype.on, arguments);
	if (!this.events.hasOwnProperty(tag)) {
		this.events[tag] = {};
	}
	newjobid = -1;
	for (var jobid in this.events[tag]) {
		newjobid = max(jobid, newjobid);
	}
	newjobid++;
	this.events[tag][newjobid] = args;
	return newjobid;
};

Registry.prototype.deregister = function deregisterEvent(tag, jobid) {
	if (this.events.hasOwnProperty(tag)) {
		if (this.events[tag].hasOwnProperty(jobid)) {
			delete this.events[tag][jobid];
			return true;
		}
	}
	return false;
};
