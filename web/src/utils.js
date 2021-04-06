// Array operations
Object.defineProperty(Array.prototype, "pushToggle", {
  enumerable: false,
  value: function(item) {
    const index = this.indexOf(item);
    if (index == -1) {
      this.push(item);
    } else {
      this.splice(index, 1);
    }
  }
});

Object.defineProperty(Array.prototype, "pushIfNotExist", {
  enumerable: false,
  value: function(item) { 
    if (!this.includes(item)) {
      this.push(item);
    }
  }
});

Object.defineProperty(Array.prototype, "popIfExist", {
  enumerable: false,
  value: function(item) { 
    const index = this.indexOf(item);
    if (index != -1) {
      this.splice(index, 1);
    }
  }
});

// Set operations
Object.defineProperty(Set.prototype, "superSet", {
  enumerable: false,
  value: function(subset) { 
    for (var elem of subset) {
      if (!this.has(elem)) {
          return false;
      }
    }
    return true;
  }
});

Object.defineProperty(Set.prototype, "union", {
  enumerable: false,
  value: function(other) { 
    var _union = new Set(this);
    for (var elem of other) {
      _union.add(elem);
    }
    return _union;
  }
});

Object.defineProperty(Set.prototype, "intersection", {
  enumerable: false,
  value: function(other) { 
    var _intersection = new Set();
    for (var elem of other) {
        if (this.has(elem)) {
          _intersection.add(elem);
        }
    }
    return _intersection;
  }
});

Object.defineProperty(Set.prototype, "simetricDiff", {
  enumerable: false,
  value: function(other) { 
    var _diff = new Set(this);
    for (var elem of other) {
        if (_diff.has(elem)) {
          _diff.delete(elem);
        } else {
          _diff.add(elem);
        }
    }
    return _diff;
  }
});

Object.defineProperty(Set.prototype, "diff", {
  enumerable: false,
  value: function(other) { 
    var _diff = new Set(this);
    for (var elem of other) {
      _diff.delete(elem);
    }
    return _diff;
  }
});