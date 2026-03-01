import { createMirrorStore } from "./mirror-store";

const store = createMirrorStore("", "initial-input");

const unsubscribe = store.subscribe((value, source) => {
  console.log(`[mirror] source=${source} value=${value}`);
});

store.setValue("first", "input-a");
store.patch((current) => current.toUpperCase(), "input-b");

unsubscribe();
