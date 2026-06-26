// utils/paginate.js
export function paginate(obj, pageSize) {
  const keys = Object.keys(obj);
  return Array.from(
    { length: Math.ceil(keys.length / pageSize) },
    (_, index) => {
      const pageKeys = keys.slice(index * pageSize, (index + 1) * pageSize);
      const pageObj = {};
      pageKeys.forEach(key => {
        pageObj[key] = obj[key];
      });
      return pageObj;
    }
  );
}
