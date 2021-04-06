// Array operations overwrite
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